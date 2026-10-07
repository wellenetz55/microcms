'use strict';
const toggle=document.querySelector('.menu-toggle');const menu=document.querySelector('.mobile-nav');
function closeMenu(){toggle.setAttribute('aria-expanded','false');toggle.setAttribute('aria-label','メニューを開く');menu.classList.remove('open');menu.querySelectorAll('details').forEach(d=>d.open=false);document.body.style.overflow='';}
toggle?.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?'メニューを閉じる':'メニューを開く');menu.classList.toggle('open',open);document.body.style.overflow=open?'hidden':'';});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&menu?.classList.contains('open')){closeMenu();toggle.focus();}});
matchMedia('(min-width:901px)').addEventListener('change',e=>{if(e.matches)closeMenu();});
const filters=document.querySelectorAll('[data-filter]'),items=document.querySelectorAll('[data-category]'),search=document.querySelector('[data-search]');let selected='all';
function filterItems(){let shown=0;const term=(search?.value||'').trim().toLocaleLowerCase();items.forEach(item=>{const match=(selected==='all'||item.dataset.category===selected)&&item.textContent.toLocaleLowerCase().includes(term);item.hidden=!match;if(match)shown++;});const count=document.querySelector('[data-count]');if(count)count.textContent=`${shown}件の事例`;const empty=document.querySelector('[data-empty]');if(empty)empty.hidden=shown>0;}
filters.forEach(b=>b.addEventListener('click',()=>{selected=b.dataset.filter;filters.forEach(f=>f.setAttribute('aria-pressed',String(f===b)));filterItems();}));search?.addEventListener('input',filterItems);
// A conceptual preview only: no external emergency system is controlled here.
document.querySelectorAll('[data-qr-demo]').forEach(demo=>{
  demo.querySelectorAll('[data-qr-mode]').forEach(button=>button.addEventListener('click',()=>{
    const mode=button.dataset.qrMode;
    demo.querySelectorAll('[data-qr-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
    demo.querySelectorAll('[data-qr-panel]').forEach(panel=>{panel.hidden=panel.dataset.qrPanel!==mode;});
    demo.querySelector('[data-qr-status]').textContent=mode==='normal'?'平時の情報提供を表示しています。':'緊急時の情報提供イメージを表示しています。';
  }));
});

// Hover on a desktop, disclosure buttons for touch and keyboard.
const desktopNavigation=document.querySelector('.desktop-nav');
const navItems=[...document.querySelectorAll('[data-nav-item]')];
const desktopWidth=matchMedia('(min-width:901px)');
let navCloseTimer;
let navKeyboardOpen=false;
function closeDropdowns(){
  clearTimeout(navCloseTimer);
  navItems.forEach(item=>{item.classList.remove('is-open');item.querySelector('.nav-disclosure').setAttribute('aria-expanded','false');item.querySelector('.nav-panel').hidden=true;});
}
function openDropdown(item,keyboard=false){
  closeDropdowns();
  if(!desktopWidth.matches)return;
  navKeyboardOpen=keyboard;
  item.classList.add('is-open');item.querySelector('.nav-disclosure').setAttribute('aria-expanded','true');item.querySelector('.nav-panel').hidden=false;
}
navItems.forEach(item=>{
  const button=item.querySelector('.nav-disclosure');
  item.addEventListener('pointerenter',event=>{if(event.pointerType==='mouse')openDropdown(item);});
  item.addEventListener('pointerleave',event=>{if(event.pointerType==='mouse'&&!navKeyboardOpen)navCloseTimer=setTimeout(closeDropdowns,220);});
  button.addEventListener('click',event=>{if(button.getAttribute('aria-expanded')==='true')closeDropdowns();else openDropdown(item,event.detail===0);});
  item.addEventListener('keydown',event=>{
    if(event.key==='Escape'&&item.classList.contains('is-open')){event.preventDefault();event.stopPropagation();closeDropdowns();button.focus();}
    else if(event.key==='ArrowDown'&&event.target.closest('.nav-top')){event.preventDefault();openDropdown(item,true);item.querySelector('.nav-panel a').focus();}
  });
});
document.addEventListener('pointerdown',event=>{if(!desktopNavigation?.contains(event.target))closeDropdowns();});
desktopNavigation?.addEventListener('focusout',()=>setTimeout(()=>{if(!desktopNavigation.contains(document.activeElement))closeDropdowns();else{const current=document.activeElement.closest('[data-nav-item]');if(current&&!current.classList.contains('is-open'))closeDropdowns();}},0));
desktopWidth.addEventListener('change',closeDropdowns);

// Homepage background playlist: reveal only playing footage, keeping the poster underneath.
(()=>{
  const layer=document.querySelector('[data-hero-videos]');
  if(!layer)return;
  const sources=JSON.parse(layer.dataset.heroVideos);
  const hero=layer.closest('.hero');
  const button=hero.querySelector('.hero-video-toggle');
  const reduced=matchMedia('(prefers-reduced-motion:reduce)');
  const videos=sources.map(src=>{
    const video=document.createElement('video');
    video.muted=true;video.defaultMuted=true;video.loop=true;video.playsInline=true;
    video.setAttribute('muted','');video.setAttribute('playsinline','');
    video.preload='none';video.tabIndex=-1;video.dataset.src=src;
    layer.append(video);return video;
  });
  const failed=new Set();
  let active=-1,pending=-1,timer,watchdog,fadeTimer,visible=true,userPaused=reduced.matches;
  const allowed=()=>visible&&!document.hidden&&!userPaused;
  const nextIndex=from=>{
    for(let n=1;n<=videos.length;n++){
      const index=(from+n)%videos.length;
      if(!failed.has(index))return index;
    }
    return -1;
  };
  function load(index){
    const video=videos[index];
    if(!video.hasAttribute('src')){video.preload='auto';video.src=video.dataset.src;video.load();}
    return video;
  }
  function label(){
    button.hidden=false;
    const text=userPaused?'背景動画を再生':'背景動画を一時停止';
    button.textContent=userPaused?'動画を再生':'動画を一時停止';
    button.setAttribute('aria-label',text);
  }
  function schedule(){
    clearTimeout(timer);
    if(allowed()&&nextIndex(active)!==active)timer=setTimeout(()=>start(nextIndex(active)),3000);
  }
  function reveal(index){
    if(index!==pending||!allowed())return;
    clearTimeout(watchdog);clearTimeout(fadeTimer);
    const previous=active;
    active=index;pending=-1;
    videos.forEach((video,i)=>video.classList.toggle('is-active',i===active));
    if(previous>=0&&previous!==active)fadeTimer=setTimeout(()=>videos[previous].pause(),350);
    label();schedule();
    const next=nextIndex(active);
    if(next>=0&&next!==active)load(next);
  }
  function failure(index){
    failed.add(index);
    if(index!==active&&index!==pending)return;
    clearTimeout(timer);clearTimeout(watchdog);
    videos[index].pause();
    if(index===active){videos[index].classList.remove('is-active');active=-1;}
    pending=-1;
    const next=nextIndex(index);
    if(next<0){button.hidden=true;return;}
    if(allowed())start(next);
  }
  function start(index){
    if(index<0||!allowed())return;
    clearTimeout(timer);clearTimeout(watchdog);
    pending=index;
    const video=load(index);
    if(index!==active&&video.readyState>0)video.currentTime=0;
    watchdog=setTimeout(()=>failure(index),8000);
    video.play().catch(error=>{
      if(pending!==index)return;
      if(error.name==='NotAllowedError'){
        clearTimeout(watchdog);pending=-1;userPaused=true;label();
      }else if(error.name!=='AbortError')failure(index);
    });
  }
  function sync(){
    clearTimeout(timer);clearTimeout(watchdog);clearTimeout(fadeTimer);
    pending=-1;
    videos.forEach(video=>video.pause());
    if(allowed())start(active>=0?active:nextIndex(-1));
  }
  videos.forEach((video,index)=>{
    video.addEventListener('playing',()=>reveal(index));
    video.addEventListener('error',()=>failure(index));
  });
  button.addEventListener('click',()=>{userPaused=!userPaused;label();sync();});
  document.addEventListener('visibilitychange',sync);
  reduced.addEventListener('change',event=>{userPaused=event.matches;label();sync();});
  new IntersectionObserver(entries=>{
    visible=entries[0].isIntersecting;sync();
  },{threshold:0}).observe(hero);
  if(userPaused)label();
})();

// Purpose-specific inquiries: review locally, then submit using form.run's native POST API.
// The SDK is optional. Never mark success until form.run handles the request.
const contactForm=document.querySelector('#contact-inquiry-form');
if(contactForm){
  const fields=document.querySelector('#contact-fields');
  const review=document.querySelector('#contact-review');
  const values=document.querySelector('#contact-review-values');
  const submit=document.querySelector('#contact-submit');
  const edit=document.querySelector('#contact-edit');
  const status=document.querySelector('#contact-submit-status');
  let confirmed=false, sending=false;
  const reset=()=>{sending=false;confirmed=false;fields.hidden=false;review.hidden=true;edit.hidden=true;edit.disabled=false;submit.disabled=false;submit.textContent='入力内容を確認する';status.textContent='';};
  reset();
  edit.addEventListener('click',()=>{reset();fields.querySelector('input').focus();});
  contactForm.addEventListener('submit',event=>{
    if(sending){event.preventDefault();return;}
    if(!contactForm.checkValidity()){event.preventDefault();reset();contactForm.reportValidity();return;}
    if(!confirmed){
      event.preventDefault();
      values.replaceChildren();
      for(const [name,value] of new FormData(contactForm)){
        if(name==='_formrun_gotcha')continue;
        const term=document.createElement('dt'),description=document.createElement('dd');
        term.textContent=name;description.textContent=value||'未入力';values.append(term,description);
      }
      confirmed=true;fields.hidden=true;review.hidden=false;edit.hidden=false;submit.textContent='この内容で送信する';
      document.querySelector('#contact-review-title').focus();
      review.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth',block:'start'});
      return;
    }
    sending=true;submit.disabled=true;edit.disabled=true;submit.textContent='送信しています…';status.textContent='form.runへ送信しています。画面が切り替わるまでお待ちください。';
    // Allow the browser's standard form submission, including form.run's error/thank-you response.
  });
  window.addEventListener('pageshow',event=>{if(event.persisted)reset();});
}
