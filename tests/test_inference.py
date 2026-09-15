"""
Unit tests for NASA-IBM LFM PyTorch inference pipeline and FlexiViT adapter.
"""

from lunar_lfm.config import MODEL_SPECS
from lunar_lfm.inference import (
    load_pretrained_lfm,
    LunarViTBackbone,
    LunarDownstreamPredictor,
    TORCH_AVAILABLE,
)


def test_load_pretrained_lfm_contract():
    """Verify load_pretrained_lfm returns a valid predictor or diagnostic structure."""
    res = load_pretrained_lfm(patch_size=16)
    if not TORCH_AVAILABLE:
        assert res["status"] == "torch_not_installed"
        assert "PyTorch is not installed" in res["message"]
        assert res["architecture"].embed_dim == 768
        assert res["architecture"].depth == 12
    else:
        assert isinstance(res, LunarDownstreamPredictor)
        assert res.backbone.embed_dim == 768
        assert res.backbone.depth == 12


def test_flexivit_patch_adaptation_dimensions():
    """Verify FlexiViT handles 8, 16, and 32 patch sizes correctly."""
    backbone = LunarViTBackbone(patch_size=16)
    backbone.set_patch_size(8)
    assert backbone.patch_size == 8
    backbone.set_patch_size(32)
    assert backbone.patch_size == 32
    backbone.set_patch_size(16)
    assert backbone.patch_size == 16


def test_offline_mode_abai_l006_compliance():
    """Verify offline_only mode raises FileNotFoundError instead of generating synthetic weights."""
    if TORCH_AVAILABLE:
        try:
            load_pretrained_lfm(
                checkpoint_path="/nonexistent/lunar_weights.pt",
                offline_only=True
            )
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    test_load_pretrained_lfm_contract()
    test_flexivit_patch_adaptation_dimensions()
    test_offline_mode_abai_l006_compliance()
    print("All inference tests passed.")
