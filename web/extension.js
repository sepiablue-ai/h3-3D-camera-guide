import {app} from '../../scripts/app.js';

app.registerExtension({
  name:'h3.camera.guide',
  async beforeRegisterNodeDef(nodeType,nodeData){
    if(nodeData.name!=='H3CameraGuide')return;
    const created=nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated=function(){
      const result=created?.apply(this,arguments);
      const node=this, stateWidget=node.widgets.find(w=>w.name==='camera_state');
      // The original STRING widget remains the serialization/API source of truth.
      stateWidget.hidden=true;stateWidget.computeSize=()=>[0,-4];
      if(stateWidget.element)stateWidget.element.style.display='none';
      const frame=document.createElement('iframe');frame.src=new URL('./editor.html',import.meta.url).href;
      frame.style.cssText='width:100%;height:100%;border:0;border-radius:8px';frame.title='H3 3D Camera Guide';
      const widget=node.addDOMWidget('camera_editor','H3_CAMERA_EDITOR',frame,{serialize:false,hideOnZoom:false});
      widget.computeSize=()=>[700,660];
      function send(){try{frame.contentWindow?.postMessage({type:'h3-camera-load',state:JSON.parse(stateWidget.value),config:Object.fromEntries(['width','height','frames','fps'].map(n=>[n,node.widgets.find(w=>w.name===n).value]))},location.origin);}catch(err){console.error('H3 Camera state:',err);}}
      const receive=e=>{if(e.source!==frame.contentWindow||e.origin!==location.origin)return;if(e.data?.type==='h3-camera-ready')send();if(e.data?.type==='h3-camera-change'){stateWidget.value=JSON.stringify(e.data.state);node.setDirtyCanvas(true,true);}};
      window.addEventListener('message',receive);
      for(const n of ['width','height','frames','fps']){const w=node.widgets.find(w=>w.name===n),old=w.callback;w.callback=function(){old?.apply(this,arguments);send();};}
      const configure=node.onConfigure;node.onConfigure=function(){configure?.apply(this,arguments);setTimeout(send,0);};
      const removed=node.onRemoved;node.onRemoved=function(){window.removeEventListener('message',receive);frame.remove();removed?.apply(this,arguments);};
      node.setSize([740,850]);return result;
    };
  }
});
