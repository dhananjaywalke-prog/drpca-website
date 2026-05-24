(function() {
    'use strict';
    
    // Show once per browser (localStorage)
    if (localStorage.getItem('drpca_disclaimer_v1')) return;
    
    // Inject styles
    var css = '\
.drpca-disclaimer-overlay{position:fixed;inset:0;background:rgba(10,22,40,0.75);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);z-index:99999;display:flex;align-items:center;justify-content:center;padding:1.5rem;opacity:0;animation:drpcaFadeIn .4s forwards}\
@keyframes drpcaFadeIn{to{opacity:1}}\
.drpca-disclaimer-modal{background:#FFFFFF;border-radius:12px;max-width:580px;width:100%;max-height:90vh;overflow-y:auto;box-shadow:0 30px 80px rgba(0,0,0,0.4);transform:translateY(20px);animation:drpcaSlideUp .5s .15s forwards;font-family:"DM Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}\
@keyframes drpcaSlideUp{to{transform:translateY(0)}}\
.drpca-disclaimer-header{padding:1.75rem 2rem 1rem;border-bottom:1px solid rgba(31,56,100,0.08);display:flex;align-items:center;gap:.75rem}\
.drpca-disclaimer-icon{width:36px;height:36px;border-radius:50%;background:rgba(184,134,11,0.12);display:flex;align-items:center;justify-content:center;flex-shrink:0}\
.drpca-disclaimer-icon svg{width:18px;height:18px;color:#B8860B}\
.drpca-disclaimer-title{font-family:"DM Serif Display",Georgia,serif;font-size:1.25rem;color:#1F3864;line-height:1.3}\
.drpca-disclaimer-body{padding:1.5rem 2rem}\
.drpca-disclaimer-body p{font-size:.85rem;line-height:1.65;color:#3d3d56;margin:0 0 .85rem}\
.drpca-disclaimer-body p:last-child{margin-bottom:0}\
.drpca-disclaimer-list{margin:0 0 .85rem 0;padding-left:0;list-style:none}\
.drpca-disclaimer-list li{position:relative;padding-left:1.25rem;font-size:.85rem;line-height:1.65;color:#3d3d56;margin-bottom:.6rem}\
.drpca-disclaimer-list li::before{content:"•";position:absolute;left:0.3rem;color:#B8860B;font-weight:700}\
.drpca-disclaimer-footer{padding:1.25rem 2rem 1.75rem;border-top:1px solid rgba(31,56,100,0.08);display:flex;justify-content:flex-end;gap:.75rem;background:#FAFBFD;border-radius:0 0 12px 12px}\
.drpca-disclaimer-btn{padding:.7rem 1.75rem;background:#1F3864;color:#FFFFFF;border:none;border-radius:8px;font-size:.85rem;font-weight:600;font-family:inherit;cursor:pointer;transition:all .25s cubic-bezier(0.4,0,0.2,1);letter-spacing:.01em}\
.drpca-disclaimer-btn:hover{background:#2E5FA3;transform:translateY(-1px);box-shadow:0 4px 12px rgba(31,56,100,0.25)}\
.drpca-disclaimer-firm{font-size:.7rem;color:#6b6b80;letter-spacing:.05em}\
@media(max-width:580px){\
.drpca-disclaimer-header,.drpca-disclaimer-body,.drpca-disclaimer-footer{padding-left:1.25rem;padding-right:1.25rem}\
.drpca-disclaimer-title{font-size:1.1rem}\
.drpca-disclaimer-footer{flex-direction:column-reverse;align-items:stretch}\
.drpca-disclaimer-btn{width:100%}\
.drpca-disclaimer-firm{text-align:center}\
}';
    
    var style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
    
    // Build HTML
    var html = '\
<div class="drpca-disclaimer-overlay" id="drpcaDisclaimer">\
    <div class="drpca-disclaimer-modal" role="dialog" aria-labelledby="drpcaDisclaimerTitle">\
        <div class="drpca-disclaimer-header">\
            <div class="drpca-disclaimer-icon">\
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>\
            </div>\
            <div class="drpca-disclaimer-title" id="drpcaDisclaimerTitle">Disclaimer</div>\
        </div>\
        <div class="drpca-disclaimer-body">\
            <p>The information on this website is for general informational purposes only. By visiting <strong>drpca.com</strong>, you acknowledge that:</p>\
            <ul class="drpca-disclaimer-list">\
                <li>You are accessing this website on your own initiative \u2014 no part of this site has been promoted, advertised, or solicited through any push communication, social media campaign, or paid advertisement.</li>\
                <li>Content on this site does not constitute solicitation of professional engagement and is not an invitation to create a professional-client relationship.</li>\
                <li>Statutory services such as audit and assurance are listed for informational purposes; the firm does not solicit such engagements.</li>\
                <li>For specific advice on your matter, please consult the firm directly.</li>\
            </ul>\
        </div>\
        <div class="drpca-disclaimer-footer">\
            <div class="drpca-disclaimer-firm">DRP &amp; Co. LLP \u00b7 FRN W100047</div>\
            <button class="drpca-disclaimer-btn" id="drpcaDisclaimerOk">I Understand</button>\
        </div>\
    </div>\
</div>';
    
    var div = document.createElement('div');
    div.innerHTML = html;
    document.body.appendChild(div.firstElementChild);
    
    // Lock scroll while visible
    document.body.style.overflow = 'hidden';
    
    // Dismiss
    document.getElementById('drpcaDisclaimerOk').addEventListener('click', function() {
        localStorage.setItem('drpca_disclaimer_v1', '1');
        var overlay = document.getElementById('drpcaDisclaimer');
        overlay.style.transition = 'opacity .3s';
        overlay.style.opacity = '0';
        setTimeout(function() {
            overlay.remove();
            document.body.style.overflow = '';
        }, 300);
    });
})();
