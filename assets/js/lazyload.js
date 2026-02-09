// Lazy loading for images
document.addEventListener('DOMContentLoaded', function() {
  // Add loading="lazy" to all images that don't have it
  const images = document.querySelectorAll('img:not([loading])');
  images.forEach(img => {
    img.setAttribute('loading', 'lazy');
  });
  
  // Add loading="lazy" to iframes
  const iframes = document.querySelectorAll('iframe:not([loading])');
  iframes.forEach(iframe => {
    iframe.setAttribute('loading', 'lazy');
  });
});
