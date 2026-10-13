/* Keep horizontal diagram navigation explicit across browser/site shortcuts. */
document.addEventListener("keydown", (event) => {
  const region = event.target instanceof Element && event.target.closest(".app-figure");
  if (event.altKey || event.metaKey || event.ctrlKey || event.shiftKey) return;
  if (region && region.scrollWidth <= region.clientWidth) return;
  if (!region || !["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
  event.preventDefault();
  if (event.key === "Home") region.scrollLeft = 0;
  else if (event.key === "End") region.scrollLeft = region.scrollWidth;
  else region.scrollLeft += event.key === "ArrowRight" ? 120 : -120;
});
