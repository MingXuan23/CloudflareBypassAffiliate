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
import{util as e}from"../js/content-util.js";import{events as n}from"../../common/analytics.js";import{dcLocalStorage as t}from"../../common/local-storage.js";import{CACHE_PURGE_SCHEME as a}from"../../sw_modules/constant.js";await chrome.runtime.sendMessage({main_op:"getFloodgateFlag",flag:"dc-cv-log-genai-marker-menu-shown",cachePurge:a.NO_CALL})&&e.sendAnalytics(n.AI_ASSISTANT_MENU_SHOWN),$(document).ready((()=>{e.translateElements(".translate"),$("#menuItem1").click((()=>{e.sendAnalytics(n.AI_ASSISTANT_MENU_OPEN_IN_ACROBAT_CLICKED);const a=t.getItem("pdfMarkerLink");a&&window.open(a,"_blank")})),$("#menuItem2").click((()=>{e.sendAnalytics(n.AI_ASSISTANT_MENU_GET_SUMMARY_CLICKED);const a=t.getItem("pdfMarkerLink");t.setItem("pdfMarkerAction","summary"),a&&window.open(a,"_blank")})),$("#menuItem3").click((()=>{e.sendAnalytics(n.AI_ASSISTANT_MENU_GET_INSIGHT_CLICKED);const a=t.getItem("pdfMarkerLink");t.setItem("pdfMarkerAction","insight"),a&&window.open(a,"_blank")}))})),chrome.runtime.onMessage.addListener((e=>{"save-pdf-marker-target"===e.main_op&&t.setItem("pdfMarkerLink",e.pdfMarkerLink)}));