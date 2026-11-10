/* No personal form data is stored in the browser or sent to analytics. */
(function () {
  'use strict';
  var cfg = window.BRANDING_LEAD_CONFIG || { mode: 'preview' };
  var preview = cfg.mode !== 'production';
  var realSubmission = cfg.mode === 'production' || cfg.mode === 'test';
  var prefix = preview ? 'preview_' : '';
  var key = prefix + 'wellenetz_branding_guide_pending_v1';
  var form = document.getElementById('leadform');
  var params = new URLSearchParams(location.search);
  var allowed = {utm_source:['facebook','instagram','meta','fb','ig'],utm_medium:['paid_social'],utm_campaign:['corporate_branding_guide'],utm_content:['ad_a','ad_b']};
  var attribution = {};
  Object.keys(allowed).forEach(function(k){var v=params.get(k);if(allowed[k].indexOf(v)>=0)attribution[k]=v;});
  function emit(name, data) {
    if (!preview && !cfg.trackingEnabled) return;
    window.dataLayer=window.dataLayer||[];
    window.dataLayer.push(Object.assign({event:prefix+'branding_guide_'+name,lead_magnet_id:'corporate_branding_guide',environment:preview?'preview':'production'},data||{}));
  }
  function writePending() {
    var id='bg_'+Date.now()+'_'+(window.crypto&&crypto.randomUUID?crypto.randomUUID():Math.random().toString(36).slice(2));
    try {sessionStorage.setItem(key,JSON.stringify({id:id,time:Date.now(),attribution:attribution}));}catch(e){}
    return id;
  }
  function consumePending() {
    try {
      var raw=sessionStorage.getItem(key);sessionStorage.removeItem(key);
      if(!raw)return null;
      var p=JSON.parse(raw),age=Date.now()-p.time;
      if(!/^bg_[0-9]+_[a-zA-Z0-9-]+$/.test(p.id)||age<0||age>=1800000)return null;
      return p;
    }catch(e){return null;}
  }
  if(form) {
    emit('lp_view',attribution);
    document.querySelectorAll('a[data-cta]').forEach(function(a){a.addEventListener('click',function(){emit('cta_click',{cta_position:a.dataset.cta});});});
    var started=false;
    form.addEventListener('focusin',function(e){if(!started&&e.target.matches('input:not([type=hidden]),select')){started=true;emit('form_start');}});
    var names={company:'会社名',name:'お名前',email:'メールアドレス',role:'役職',issue:'現在の主な課題',consent:'個人情報の取扱いへの同意'};
    if(realSubmission && /^https:\/\/form\.run\/api\/v1\/r\/[a-zA-Z0-9]+$/.test(cfg.formAction||'')) {
      form.action=cfg.formAction;form.method='post';form.acceptCharset='UTF-8';
      Object.keys(names).forEach(function(k){var input=form.elements.namedItem(k);if(input)input.name=names[k];});
      var fields=Object.assign({資料種別:'企業ブランディング実践ステップガイド',お問い合わせ元ページ:cfg.publicBase},attribution);
      Object.keys(fields).forEach(function(k){var input=document.createElement('input');input.type='hidden';input.name=k;input.value=fields[k];form.appendChild(input);});
    }
    form.addEventListener('submit',function(e){
      if(!form.checkValidity()){e.preventDefault();form.reportValidity();return;}
      if(form.elements.namedItem('_formrun_gotcha').value){e.preventDefault();return;}
      if(realSubmission && !/^https:\/\/form\.run\/api\/v1\/r\/[a-zA-Z0-9]+$/.test(cfg.formAction||'')) {
        e.preventDefault();document.getElementById('submit-status').textContent='現在、受付の準備中です。時間をおいて再度お試しください。';return;
      }
      var id=writePending();emit('submit_attempt',{event_id:id});
      if(!realSubmission){e.preventDefault();form.reset();location.assign(cfg.thanksPath||'thanks.html');return;}
      form.querySelector('button[type=submit]').disabled=true;
      document.getElementById('submit-status').textContent='送信しています。完了画面へ移動するまでお待ちください。';
    });
    var ready = !realSubmission || /^https:\/\/form\.run\/api\/v1\/r\/[a-zA-Z0-9]+$/.test(cfg.formAction||'');
    form.querySelector('button[type=submit]').disabled = !ready;
    window.addEventListener('pageshow',function(){var b=form.querySelector('button[type=submit]');if(b)b.disabled=!ready;});
  }
  var download=document.getElementById('download-guide');
  if(download){
    var pending=consumePending();
    if(pending){
      document.getElementById('completion-title').textContent=preview?'資料請求完了のプレビュー':'資料をご請求いただき、ありがとうございます。';
      emit('lead_complete',{event_id:pending.id,ad_variant:pending.attribution&&pending.attribution.utm_content||'unknown'});
    }
    if(cfg.downloadPath)download.href=cfg.downloadPath;
    download.addEventListener('click',function(){emit('download_click',{delivery_channel:'completion_page'});});
    if(!preview){document.querySelector('.review').hidden=true;document.getElementById('completion-note').hidden=true;}
  }
})();
