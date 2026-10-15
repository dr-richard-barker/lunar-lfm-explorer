# Shackleton Crater: Context for the NASA-IBM LFM Explorer

This note replaces `SHACKLETON_ARTEMIS4_ANALYSIS.md` (removed 2026-10-15). That document gave
slope, illumination, Earth-visibility, rock-abundance and safety figures for four "landing zones"
that were typed into a script with no source, and an "optimal touchdown site" ranking. It also put
Shackleton's centre at 89.9°S, 0.0°E. None of that is repeated here.

## The crater

Shackleton is centred at **89.67°S, 129.78°E** with a diameter of **20.92 km**
([IAU Gazetteer of Planetary Nomenclature, feature 5450](https://planetarynames.wr.usgs.gov/Feature/5450)).

Depth, floor temperature and wall slopes are not given here. **TODO:** add them only with a cited
LOLA or Diviner source.

## Candidate landing regions nearby

| Region | NASA Artemis III list, 19 Aug 2022 (13 regions) | NASA update, 28 Oct 2024 (9 regions) |
|---|---|---|
| Connecting Ridge | yes | no |
| Peak Near Shackleton | yes | no |
| Connecting Ridge Extension | yes | no |

Sources: [NASA, 19 Aug 2022](https://www.nasa.gov/news-release/nasa-identifies-candidate-regions-for-landing-next-americans-on-moon/);
[NASA, 28 Oct 2024](https://www.nasa.gov/news-release/nasa-provides-update-on-artemis-iii-moon-landing-regions/).
Machine-readable copy: `tables/shackleton_candidate_regions.csv`, written by `scripts/shackleton_context.py`.

## Lighting at the pole

At Shackleton's latitude the Sun is never more than about 1.9° above the horizon: the crater
centre is 0.33° from the pole, and the Moon's equator is tilted about 1.54° to the ecliptic
(6.68° obliquity to its orbit minus 5.145° orbital inclination, both from the
[NASA Moon Fact Sheet](https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html), which by
Cassini's laws combine this way). Topography is ignored in this estimate. Long
shadows therefore dominate polar imagery, and the illumination geometry changes the appearance of
the same terrain from image to image.

## What the NASA-IBM LFM does with this, according to its model card

- Each tile's illumination angles (incidence, emission, phase, azimuth), sub-solar and tile-centre
  coordinates are binned and given to the encoder as text tokens alongside the image, so the model
  is handed the dominant illumination confound rather than inferring it.
- WAC-anchored (~100 m/px) and NAC-anchored (~1 m/px) tiles are separate sample families: "the two
  families are never mixed within a sample". A NAC sample's terrain layers are NAC-stereo DTM
  products (3 m), not SLDEM2015.
- FlexiViT lets the checkpoint be fine-tuned at other patch sizes; the card's benchmark results use
  patch size 8.
- The model is **"not validated for operational decisions such as landing-site certification or
  hazard clearance"**. The card reports no landing-hazard or shadow-disambiguation evaluation, and
  this repository has run none.

Model card: <https://huggingface.co/nasa-ibm-ai4science/NASA-IBM-Lunar-Foundation-Model>

## Inspecting the source data

LROC QuickMap (ACT-REACT) shows the LROC NAC polar mosaics, LOLA slope and PSR products and Diviner
temperatures for these regions:
<https://quickmap.lroc.im-ldi.com/?extent=-180,-90,180,-85&proj=10>

## The 3D models in this repository

The Blender models (`scripts/blender/`) are schematic: an analytic bowl with a 21 km rim diameter,
rim +1.2 km and floor −3.8 km (5.0 km relief in the model), plus a smooth ridge at 135° azimuth.
They are not derived from LOLA or SLDEM2015 data. Their 85° and 70° incidence lighting does not
occur at Shackleton, and the renders have not been run through the model
(`results/blender_render_inventory.json`).
