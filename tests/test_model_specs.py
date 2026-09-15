"""
Unit tests for ViT-B architecture, FlexiViT patch resizing, and tokenizer specifications.
"""

try:
    import pytest
except ImportError:
    pytest = None

from lunar_lfm.config import MODEL_SPECS
from lunar_lfm.model_inspect import ModelArchitecture, TokenizerSpecs, compute_patch_grid


def test_vit_b_dimensions():
    """Verify standard ViT-B configuration matches model card."""
    arch = ModelArchitecture()
    assert arch.embed_dim == 768
    assert arch.encoder_depth == 12
    assert arch.encoder_heads == 12
    assert arch.decoder_depth == 12
    assert arch.input_size == (256, 256)
    assert arch.pretrain_patch_size == (16, 16)


def test_flexivit_patch_grid_calculations():
    """Verify dynamic patch grid calculation for FlexiViT."""
    arch = ModelArchitecture()

    # Pretraining patch size 16x16: 256/16 = 16 patches per side = 256 patches total
    h16, w16, total16 = arch.compute_patch_grid((16, 16))
    assert (h16, w16) == (16, 16)
    assert total16 == 256

    # Downstream high-res patch size 8x8: 256/8 = 32 patches per side = 1024 patches total
    h8, w8, total8 = arch.compute_patch_grid((8, 8))
    assert (h8, w8) == (32, 32)
    assert total8 == 1024

    # Fast inference patch size 32x32: 256/32 = 8 patches per side = 64 patches total
    h32, w32, total32 = arch.compute_patch_grid((32, 32))
    assert (h32, w32) == (8, 8)
    assert total32 == 64


def test_sequence_length_fusion():
    """Verify sequence length arithmetic with multi-modal late fusion."""
    arch = ModelArchitecture()
    # 5 WAC dense modalities, 16x16 patch size: 5 * 256 = 1,280 tokens
    # + 8 optical metadata sequence tokens
    # + 28 static context sequence tokens
    # Total = 1,280 + 8 + 28 = 1,316 tokens
    seq = arch.compute_sequence_length(num_dense_modalities=5, patch_size=(16, 16))
    assert seq["dense_tokens"] == 1280
    assert seq["optical_metadata_tokens"] == 8
    assert seq["static_context_tokens"] == 28
    assert seq["total_sequence_length"] == 1316


def test_tokenizer_fsq_codebook():
    """Verify FSQ tokenizer specifications and total states."""
    tok = TokenizerSpecs(modality_key="vis")
    assert tok.quantizer == "FSQ"
    assert tok.fsq_levels == (8, 8, 8, 6, 5)
    # 8 * 8 * 8 * 6 * 5 = 15,360 codebook states
    computed_states = 1
    for lvl in tok.fsq_levels:
        computed_states *= lvl
    assert computed_states == 15360
    assert tok.num_codebook_states == 15360
    assert tok.decoder_type == "DDPM"
