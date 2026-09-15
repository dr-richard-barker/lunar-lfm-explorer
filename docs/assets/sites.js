/* ============================================================================
   COSE — shared site registry for estate navigation.
   ========================================================================== */
window.BARKER_SITES = {
  brand: { name:"COSE", url:"https://cosecloud.com/", logo:"assets/cose-logo.png" },
  hub: "https://dr-richard-barker.github.io/CoSE_Cloud/Hub/",
  groups: [
    {
      name: "Planetary Science & Lunar Models",
      items: [
        { id:"lunar-lfm-explorer", emoji:"🌕", title:"NASA-IBM Lunar Foundation Model",
          desc:"FAIR multimodal remote sensing explorer for ViT-B trained on SomBench",
          url:"https://dr-richard-barker.github.io/lunar-lfm-explorer/" },
        { id:"LunarFarm-BLSS", emoji:"🚜", title:"LunarFarm BLSS",
          desc:"Bioregenerative life support simulation on lunar surface",
          url:"https://dr-richard-barker.github.io/LunarFarm-BLSS/" },
        { id:"LunarLeaf-CFD", emoji:"🍃", title:"Lunar LEAF — Photorespiration",
          desc:"CFD model of photorespiration in a lunar growth chamber",
          url:"https://dr-richard-barker.github.io/LunarLeaf-CFD/" },
        { id:"AstroRegolith", emoji:"🌑", title:"AstroRegolith",
          desc:"Open database and growth-anchored reanalysis of plant growth in regolith",
          url:"https://dr-richard-barker.github.io/AstroRegolith/" }
      ]
    },
    {
      name: "Space Biology & Decoders",
      items: [
        { id:"Plant_response_to_radiation", emoji:"☢️", title:"Plant Response to Radiation",
          desc:"Transcriptomic kinetic atlas of ionizing radiation response",
          url:"https://dr-richard-barker.github.io/Plant_response_to_radiation/" },
        { id:"AstroMycology", emoji:"🍄", title:"AstroMycology",
          desc:"Comparative genomics and radiation response in space fungi",
          url:"https://dr-richard-barker.github.io/AstroMycology/" }
      ]
    }
  ]
};
