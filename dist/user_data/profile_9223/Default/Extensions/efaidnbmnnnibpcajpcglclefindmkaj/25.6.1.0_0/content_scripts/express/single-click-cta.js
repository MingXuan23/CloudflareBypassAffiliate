/*************************************************************************
* ADOBE CONFIDENTIAL
* ___________________
*
*  Copyright 2015 Adobe Systems Incorporated
*  All Rights Reserved.
*
* NOTICE:  All information contained herein is, and remains
* the property of Adobe Systems Incorporated and its suppliers,
* if any.  The intellectual and technical concepts contained
* herein are proprietary to Adobe Systems Incorporated and its
* suppliers and are protected by all applicable intellectual property laws,
* including trade secret and or copyright laws.
* Dissemination of this information or reproduction of this material
* is strictly forbidden unless prior written permission is obtained
* from Adobe Systems Incorporated.
**************************************************************************/
import expressFteUtils from"./express-fte-utils.js";class SingleClickCTA{ENTRY_POINT_BUTTON_CLASS="cc440d50ba-express-entrypoint-button";ENTRY_POINT_BUTTON_ICON_IMG_CLASS="cc440d50ba-express-entrypoint-button-icon-img";ENTRY_POINT_BUTTON_TOOLTIP_CLASS="cc440d50ba-tooltiptext";constructor(){this.init()}async init(){this.htmlDataPromise=fetch(chrome.runtime.getURL("resources/express/expressSingleClickCTA.html")).then((e=>e.text())).then((e=>{this.htmlData=e})),expressFteUtils.addFontToDocument()}async renderMenuButton(e,t){await this.htmlDataPromise;const s=document.createElement("div");s.innerHTML=this.htmlData,s.className=t;const n=s.getElementsByClassName(this.ENTRY_POINT_BUTTON_CLASS)[0];n.onclick=()=>{const s="editImage";expressFteUtils.sendAnalyticsEvent([["DCBrowserExt:Express:SingleCTA:VERB:Clicked",{domain:domain,VERB:s,expressTouchpoint:t}]]),e(s)};n.getElementsByClassName(this.ENTRY_POINT_BUTTON_ICON_IMG_CLASS)[0].src=chrome.runtime.getURL("browser/images/acrobat_prodc_appicon_24.svg"),util.translateElements(".translate",s);const i=n.getElementsByClassName(this.ENTRY_POINT_BUTTON_TOOLTIP_CLASS)[0];return s.addEventListener("mouseenter",(()=>{const e=s.offsetWidth/2-i.offsetWidth/2;i.style.left=`${e}px`})),s}}const expressSingleClickCTA=new SingleClickCTA;export default expressSingleClickCTA;