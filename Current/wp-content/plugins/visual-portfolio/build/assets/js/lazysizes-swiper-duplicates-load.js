!function(e,t){const i=function(){t(e.lazySizes),e.removeEventListener("lazyunveilread",i,!0)};t=t.bind(null,e,e.document),e.lazySizes?i():e.addEventListener("lazyunveilread",i,!0)}(window,((e,t,i)=>{if(!e.addEventListener)return;const{unveil:d}=i.loader,n={getSlideData(e){const t=e.closest(".swiper-slide"),i=!!t&&t.getAttribute("data-swiper-slide-index");return{$el:t,slideIndex:i}},run(e){const t=this.getSlideData(e);var i,n;return t.slideIndex&&(i=t.$el,n=`[data-swiper-slide-index="${t.slideIndex}"]`,[...i.parentNode.children].filter((e=>1===e.nodeType&&e!==i&&(!n||e.matches(n))))).forEach((e=>{const t=e.querySelectorAll("img.vp-lazyload, img.vp-lazyloading");t&&t.forEach((e=>{d(e)}))})),!0}};i.swiperDuplicatesLoad=n,t.addEventListener("lazyloaded",(e=>{if(e.defaultPrevented||!e.detail||e.detail.swiperDuplicatesChecked||!e.target||e.detail.instance!==i)return;const t=e.target;e.detail.swiperDuplicatesChecked=n.run(t)}))}));