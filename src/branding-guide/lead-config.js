window.BRANDING_LEAD_CONFIG = {
  "mode": "production",
  "formAction": "https://form.run/api/v1/r/7i2n9qwtdwk8mmdozsoyld6t",
  "thanksPath": "/branding/practical-guide/thanks/",
  "downloadPath": "/branding/practical-guide/guide.pdf",
  "campaign": "corporate_branding_guide",
  "publicBase": "https://www.wellenetz.co.jp/branding/practical-guide/",
  "trackingEnabled": true
};
// Local file inspection must never submit to the live endpoint.
if(location.hostname!=="www.wellenetz.co.jp"){window.BRANDING_LEAD_CONFIG.mode="preview";window.BRANDING_LEAD_CONFIG.formAction="";window.BRANDING_LEAD_CONFIG.trackingEnabled=false;}
