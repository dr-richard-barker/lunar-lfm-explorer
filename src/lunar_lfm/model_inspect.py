"""
Model architecture and tokenizer inspection utilities for the NASA-IBM Lunar Foundation Model.

Enables inspecting ViT-B encoder-decoder configurations, FlexiViT patch grids,
tokenizer FSQ levels, and parameter estimates without needing the 12.8 GB weights in RAM.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Any
from lunar_lfm.config import MODEL_SPECS, ModelSpecs


@dataclass(frozen=True)
class TokenizerSpecs:
    """Specification for a modality-specific VQ-VAE tokenizer."""
    modality_key: str
    quantizer: str = "FSQ"  # Finite Scalar Quantization
    fsq_levels: Tuple[int, ...] = (8, 8, 8, 6, 5)
    num_codebook_states: int = 15_360  # 8 * 8 * 8 * 6 * 5
    decoder_type: str = "DDPM"  # Denoising Diffusion Probabilistic Model
    downsample_factor: int = 4  # e.g., 256x256 -> 64x64 discrete token grid


@dataclass
class ModelArchitecture:
    """Ground-truth architecture representation of NASA-IBM LFM."""
    backbone_name: str = MODEL_SPECS.backbone_type
    embed_dim: int = MODEL_SPECS.embed_dim
    encoder_depth: int = MODEL_SPECS.depth
    encoder_heads: int = MODEL_SPECS.num_heads
    decoder_depth: int = MODEL_SPECS.decoder_depth
    decoder_heads: int = MODEL_SPECS.decoder_heads
    input_size: Tuple[int, int] = MODEL_SPECS.input_size
    pretrain_patch_size: Tuple[int, int] = MODEL_SPECS.pretrain_patch_size

    def compute_patch_grid(self, patch_size: Tuple[int, int]) -> Tuple[int, int, int]:
        """
        Compute (num_patches_h, num_patches_w, total_patches) for a given patch size.
        Supports FlexiViT dynamic resizing.
        """
        h_patches = self.input_size[0] // patch_size[0]
        w_patches = self.input_size[1] // patch_size[1]
        return (h_patches, w_patches, h_patches * w_patches)

    def compute_sequence_length(
        self,
        num_dense_modalities: int,
        patch_size: Tuple[int, int],
        has_optical_metadata: bool = True,
        has_static_context: bool = True,
    ) -> Dict[str, int]:
        """
        Calculate token sequence lengths for multi-modal late fusion.
        Tokens are concatenated along the sequence dimension.
        """
        _, _, patches_per_modality = self.compute_patch_grid(patch_size)
        dense_tokens = num_dense_modalities * patches_per_modality
        optical_tokens = 8 if has_optical_metadata else 0
        context_tokens = 28 if has_static_context else 0
        total_tokens = dense_tokens + optical_tokens + context_tokens

        return {
            "patches_per_modality": patches_per_modality,
            "num_dense_modalities": num_dense_modalities,
            "dense_tokens": dense_tokens,
            "optical_metadata_tokens": optical_tokens,
            "static_context_tokens": context_tokens,
            "total_sequence_length": total_tokens,
        }

    def estimate_parameter_breakdown(self) -> Dict[str, Any]:
        """
        Analytical parameter breakdown for ViT-B encoder and decoder components.
        """
        d = self.embed_dim
        # Standard ViT layer:
        # LayerNorm1: 2*d
        # Multi-Head Attention: Q, K, V projections (3 * d * d + 3*d) + Out proj (d*d + d) = 4*d^2 + 4*d
        # LayerNorm2: 2*d
        # MLP: Linear1 (d * 4d + 4d) + Linear2 (4d * d + d) = 8*d^2 + 5*d
        # Total per layer approx: 12 * d^2 + 13*d
        layer_params = 12 * (d ** 2) + 13 * d

        encoder_layers_params = self.encoder_depth * layer_params
        decoder_layers_params = self.decoder_depth * layer_params

        # Modality patch embed projections (per modality):
        # 16x16 patch * channels * d
        # Average dense modalities ~ 5 channels: 5 * 256 * 768 = ~1M params
        patch_adapters_approx = 9 * (5 * 256 * d)

        total_approx = encoder_layers_params + decoder_layers_params + patch_adapters_approx

        return {
            "encoder_layers_params": encoder_layers_params,
            "decoder_layers_params": decoder_layers_params,
            "encoder_layer_count": self.encoder_depth,
            "decoder_layer_count": self.decoder_depth,
            "hidden_dimension": self.embed_dim,
            "attention_heads": self.encoder_heads,
            "approx_backbone_params_millions": round(total_approx / 1e6, 2),
            "estimated_bf16_weight_gb": round((total_approx * 2) / (1024 ** 3), 2),
        }


def compute_patch_grid(
    input_size: Tuple[int, int] = (256, 256),
    patch_size: Tuple[int, int] = (16, 16)
) -> Tuple[int, int, int]:
    """Helper to compute grid patches and count."""
    h_patches = input_size[0] // patch_size[0]
    w_patches = input_size[1] // patch_size[1]
    return (h_patches, w_patches, h_patches * w_patches)


def estimate_parameter_counts() -> Dict[str, Any]:
    """Return ground truth analytical parameter estimates."""
    arch = ModelArchitecture()
    return arch.estimate_parameter_breakdown()
