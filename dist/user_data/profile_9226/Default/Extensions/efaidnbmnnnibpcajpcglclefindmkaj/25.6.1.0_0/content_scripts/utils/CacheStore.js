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
class CacheStore{constructor(e="default-cache"){this.cacheName=e}async set(e,t){try{if("undefined"==typeof caches)return null;const a=await caches.open(this.cacheName);await(a?.put?.(e,new Response(JSON.stringify(t))))}catch(e){console.error("Cache set failed:",e)}}async setWithTTL(e,t,a){try{const c=Date.now()+a;await chrome.storage.local.set({[`${this.cacheName}-${e}-expiry`]:c}),await this.set(e,t)}catch(e){console.error("Cache setWithTTL failed:",e)}}async get(e){try{if("undefined"==typeof caches)return null;const t=await caches.open(this.cacheName),a=await(t?.match?.(e));return a?await a.json():null}catch(e){return console.error("Cache get failed:",e),null}}async getWithTTL(e){try{const t=`${this.cacheName}-${e}-expiry`,a=(await chrome.storage.local.get(t))[t];return a&&Date.now()>a?(this.delete(e),null):await this.get(e)}catch(e){return console.error("Cache getWithTTL failed:",e),null}}async delete(e){try{if("undefined"==typeof caches)return;const t=await caches.open(this.cacheName);await(t?.delete?.(e)),await chrome.storage.local.remove(`${this.cacheName}-${e}-expiry`)}catch(e){console.error("Cache delete failed:",e)}}}