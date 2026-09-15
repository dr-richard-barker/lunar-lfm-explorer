document.addEventListener('DOMContentLoaded', () => {
  console.log("CoSE Theme Initialized");
  // Auto-detect theme preference
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.body.setAttribute('data-theme', 'dark');
  }
});
