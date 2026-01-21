// Blog Post Enhancements: Copy Button, TOC & Reading Time
document.addEventListener('DOMContentLoaded', function() {
    // Get post content element (used by multiple features)
    const postContent = document.querySelector('.post-content');
    
    // Reading Time Calculation
    const readingTimeEl = document.getElementById('reading-time-value');
    if (postContent && readingTimeEl) {
        const text = postContent.textContent || '';
        const charCount = text.replace(/\s/g, '').length;
        const readingTime = Math.ceil(charCount / 500); // ~500 chars/min for Chinese
        readingTimeEl.textContent = readingTime;
    }
    
    // Copy Button
    const codeBlocks = document.querySelectorAll('.post-content pre');
    
    codeBlocks.forEach(function(pre) {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.textContent = 'Copy';
        
        copyBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const code = pre.querySelector('code');
            const text = code ? code.textContent : pre.textContent;
            
            function fallbackCopy(text) {
                const textarea = document.createElement('textarea');
                textarea.value = text;
                textarea.style.position = 'fixed';
                textarea.style.left = '-9999px';
                textarea.style.top = '0';
                document.body.appendChild(textarea);
                textarea.focus();
                textarea.select();
                
                try {
                    document.execCommand('copy');
                    return true;
                } catch (err) {
                    return false;
                } finally {
                    document.body.removeChild(textarea);
                }
            }
            
            function onSuccess() {
                copyBtn.classList.add('copied', 'click-effect');
                copyBtn.textContent = '✓ Copied!';
                setTimeout(function() { copyBtn.classList.remove('click-effect'); }, 300);
                setTimeout(function() {
                    copyBtn.textContent = 'Copy';
                    copyBtn.classList.remove('copied');
                }, 2000);
            }
            
            function onError() {
                copyBtn.textContent = '✗ Failed';
                copyBtn.classList.add('error');
                setTimeout(function() {
                    copyBtn.textContent = 'Copy';
                    copyBtn.classList.remove('error');
                }, 2000);
            }
            
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(text).then(onSuccess).catch(function() {
                    if (fallbackCopy(text)) onSuccess(); else onError();
                });
            } else {
                if (fallbackCopy(text)) onSuccess(); else onError();
            }
        });
        
        pre.appendChild(copyBtn);
    });

    // TOC Sidebar
    const tocSidebar = document.getElementById('toc-sidebar');
    const tocToggle = document.getElementById('toc-toggle');
    const tocContentEl = document.getElementById('toc-content');
    
    if (!tocSidebar || !tocContentEl || !postContent) return;
    
    const headings = postContent.querySelectorAll('h2, h3, h4');
    if (headings.length === 0) {
        tocSidebar.style.display = 'none';
        return;
    }
    
    // Build TOC structure
    let tocHTML = '';
    let currentH2Group = null;
    let currentH3Group = null;
    let h2Index = 0;
    let h3Index = 0;
    
    headings.forEach(function(heading, index) {
        // Generate ID if not exists
        if (!heading.id) {
            heading.id = 'heading-' + index;
        }
        
        const level = parseInt(heading.tagName.charAt(1));
        const text = heading.textContent.trim();
        const id = heading.id;
        
        if (level === 2) {
            // Close previous groups
            if (currentH3Group !== null) tocHTML += '</div>';
            if (currentH2Group !== null) tocHTML += '</div>';
            
            h2Index++;
            h3Index = 0;
            tocHTML += '<div class="toc-item level-2 has-children" data-target="' + id + '" data-group="h2-' + h2Index + '">' + text + '</div>';
            tocHTML += '<div class="toc-group" id="h2-group-' + h2Index + '">';
            currentH2Group = h2Index;
            currentH3Group = null;
        } else if (level === 3) {
            // Close previous h3 group
            if (currentH3Group !== null) tocHTML += '</div>';
            
            h3Index++;
            tocHTML += '<div class="toc-item level-3 has-children" data-target="' + id + '" data-group="h3-' + h2Index + '-' + h3Index + '">' + text + '</div>';
            tocHTML += '<div class="toc-group" id="h3-group-' + h2Index + '-' + h3Index + '">';
            currentH3Group = h3Index;
        } else if (level === 4) {
            tocHTML += '<div class="toc-item level-4" data-target="' + id + '">' + text + '</div>';
        }
    });
    
    // Close remaining groups
    if (currentH3Group !== null) tocHTML += '</div>';
    if (currentH2Group !== null) tocHTML += '</div>';
    
    tocContentEl.innerHTML = tocHTML;
    
    // Collapse all groups initially (show only h2)
    const allGroups = tocContentEl.querySelectorAll('.toc-group');
    const allParents = tocContentEl.querySelectorAll('.toc-item.has-children');
    allGroups.forEach(function(group) {
        group.classList.add('collapsed');
    });
    allParents.forEach(function(item) {
        item.classList.add('collapsed');
    });
    
    // Toggle sidebar collapse
    tocToggle.addEventListener('click', function() {
        tocSidebar.classList.toggle('collapsed');
    });
    
    // Handle item clicks
    tocContentEl.addEventListener('click', function(e) {
        const item = e.target.closest('.toc-item');
        if (!item) return;
        
        const targetId = item.getAttribute('data-target');
        const groupId = item.getAttribute('data-group');
        
        // If has children, toggle collapse
        if (item.classList.contains('has-children') && groupId) {
            const groupPrefix = groupId.startsWith('h2-') ? 'h2-group-' : 'h3-group-';
            const groupNum = groupId.replace('h2-', '').replace('h3-', '');
            const group = document.getElementById(groupPrefix + groupNum);
            
            if (group) {
                item.classList.toggle('collapsed');
                group.classList.toggle('collapsed');
            }
        }
        
        // Scroll to target
        if (targetId) {
            const target = document.getElementById(targetId);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    });
    
    // Highlight current section on scroll
    let ticking = false;
    const tocItems = tocContentEl.querySelectorAll('.toc-item');
    
    function updateActiveItem() {
        const scrollPos = window.scrollY + 120;
        let currentHeading = null;
        
        headings.forEach(function(heading) {
            if (heading.offsetTop <= scrollPos) {
                currentHeading = heading;
            }
        });
        
        tocItems.forEach(function(item) {
            item.classList.remove('active');
            if (currentHeading && item.getAttribute('data-target') === currentHeading.id) {
                item.classList.add('active');
            }
        });
        
        ticking = false;
    }
    
    window.addEventListener('scroll', function() {
        if (!ticking) {
            requestAnimationFrame(updateActiveItem);
            ticking = true;
        }
    });
    
    // Initial highlight
    updateActiveItem();
});
