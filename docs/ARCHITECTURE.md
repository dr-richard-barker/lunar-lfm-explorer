# NASA-IBM Lunar Foundation Model: Architecture & Methodology Deep Dive

The **NASA-IBM Lunar Foundation Model (NASA-IBM LFM)** is a multimodal, multi-resolution foundation model designed specifically for lunar remote sensing, developed under the NASA-IBM AI for Science collaboration.

---

## 1. Backbone Architecture: Vision Transformer Encoder-Decoder

| Parameter | Specification | Description |
|---|---|---|
| **Backbone Family** | ViT-B (Vision Transformer Base) | Standard transformer encoder with bidirectional self-attention |
| **Embedding Dimension ($d$)** | 768 | Width of token representations across all 12 layers |
| **Encoder Depth** | 12 Layers | Transformer encoder blocks |
| **Attention Heads** | 12 Heads | 64 dimensions per attention head |
| **MLP Ratio** | 4.0 | Feed-forward dimension = $768 \times 4 = 3,072$ |
| **Decoder Architecture** | 12-layer Transformer | Shared width with encoder, used during pretraining for masked-token reconstruction |
| **Pretraining Input Resolution** | $256 \times 256$ pixels | Fixed spatial grid per tile |
| **Pretraining Patch Size** | $16 \times 16$ pixels | Yields $16 \times 16 = 256$ patches per dense modality |
| **Parameter Count** | ~85M encoder layers (analytic estimate) | Standard ViT-B arithmetic from `model_inspect.py`; the model card gives no count. The released backbone checkpoint is 2.43 GB. |

---

## 2. FlexiViT Patch Embedding Resizing

A key capability of NASA-IBM LFM is **FlexiViT** patch embedding. While traditional ViTs require fixed patch sizes during both pretraining and fine-tuning:

$$\text{Patches per side} = \frac{\text{Input Dimension}}{\text{Patch Size}}$$

- **Pretraining ($16 \times 16$):** $256 / 16 = 16 \times 16 = 256$ patches per modality.
- **High-Resolution Fine-Tuning ($8 \times 8$):** $256 / 8 = 32 \times 32 = 1,024$ patches per modality. Provides $4\times$ denser spatial tokenization; the model card's benchmark results use this patch size.
- **Fast Inference ($32 \times 32$):** $256 / 32 = 8 \times 8 = 64$ patches per modality. Reduces attention compute by $16\times$.

FlexiViT resizes the patch projection weights so the checkpoint can be fine-tuned at other patch sizes without retraining the backbone (model card).

---

## 3. Tokenizer Design: Finite Scalar Quantization (FSQ) & DDPM

Dense imagery modalities are converted into discrete tokens using 9 dedicated VQ-VAE tokenizers trained per modality:
- **Quantization:** Finite Scalar Quantization (FSQ) with levels $(8, 8, 8, 6, 5)$.
- **Codebook Size:** $8 \times 8 \times 8 \times 6 \times 5 = 15,360$ discrete states. Unlike traditional Vector Quantization (which suffers from codebook collapse and dead codes), FSQ maps continuous latents directly into a bounded integer lattice without a learned dictionary.
- **Decoder:** Denoising Diffusion Probabilistic Model (DDPM) decoder for continuous image reconstruction from discrete token states.

---

## 4. Sequence Late Fusion & Acquisition Geometry

Traditional remote sensing models concatenate diverse bands into an $N$-channel image at the input stem. NASA-IBM LFM instead adopts **token-level late fusion**:

1. **Dense Modalities:** Each modality passes through its own modality-specific patch embedding, generating a patch token sequence.
2. **Optical metadata sequence (8 fields, at most 10 tokens):** illumination angles (incidence, emission, phase, azimuth) and coordinates are binned, stringified and text-tokenized.
3. **Static-map context sequence (28 fields, at most 31 tokens):** Diviner thermophysics, LOLA products, Mini-RF, Kaguya mineralogy, LROC WAC, GRAIL and Lunar Prospector values are footprint-averaged, binned and text-tokenized.

$$\text{Sequence} = [\mathbf{T}_{\text{vis}} \,\|\, \mathbf{T}_{\text{uv}} \,\|\, \mathbf{T}_{\text{dtm}} \,\|\, \mathbf{T}_{\text{slope}} \,\|\, \mathbf{T}_{\text{aspect}} \,\|\, \mathbf{T}_{\text{optical}} \,\|\, \mathbf{T}_{\text{context}}]$$

For 5 WAC dense modalities at $16\times16$ patch size:
$$\text{Dense tokens} = 5 \times 256 = 1,280, \quad \text{total} \le 1,280 + 10 + 31 = 1,321$$

The context limits are the `max_length` values (10 and 31) in the released `backbone/config.yaml`.
A context field is not one token: values are binned and stringified before text tokenization.

Modality-wise tokenization lets users drop or add modalities at fine-tuning time (model card).
