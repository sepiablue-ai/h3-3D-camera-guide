import * as THREE from './vendor/three.module.mjs';
import {OrbitControls} from './vendor/OrbitControls.mjs';
import {TransformControls} from './vendor/TransformControls.mjs';
import {DEFAULT,sample,basis} from './camera.mjs';

const $=id=>document.getElementById(id);
let state=structuredClone(DEFAULT), config={width:576,height:1024,frames:124,fps:24,subject_shape:'mannequin',floor_cues:'plain',source_mode:'render'};
let time=0,pose=sample(state,0),playing=false,dirty=false,updating=false;
const world=new THREE.Scene(),clean=new THREE.Scene();
world.background=new THREE.Color('#202c3e'); clean.background=new THREE.Color(.91,.93,.96);
const contentGroups=[];
function buildScene(parentScene) {
  const scene=new THREE.Group();parentScene.add(scene);contentGroups.push([parentScene,scene]);
  scene.add(new THREE.HemisphereLight(0xffffff,0x687080,2));
  const sun=new THREE.DirectionalLight(0xffffff,2);sun.position.set(4,8,5);scene.add(sun);
  const body=new THREE.MeshStandardMaterial({color:new THREE.Color(.18,.42,.60),roughness:1});
  function sphere(p,r,mat){const m=new THREE.Mesh(new THREE.SphereGeometry(r,20,12),mat);m.position.fromArray(p);scene.add(m);}
  function bone(a,b,r){const start=new THREE.Vector3(...a),end=new THREE.Vector3(...b),d=end.clone().sub(start);const m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,d.length(),12,1,true),body);m.position.copy(start).add(end).multiplyScalar(.5);m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),d.normalize());scene.add(m);sphere(a,r,body);sphere(b,r,body);}
  if(config.subject_shape==='ball')sphere([0,1,0],.95,body);
  else {
  bone([0,.92,0],[0,1.50,0],.11);bone([-.27,1.43,0],[.27,1.43,0],.075);
  for(const s of [-1,1]){bone([s*.27,1.43,0],[s*.42,1.10,0],.055);bone([s*.42,1.10,0],[s*.50,.83,.08],.05);bone([s*.12,.95,0],[s*.19,.50,0],.075);bone([s*.19,.50,0],[s*.23,.10,0],.06);bone([s*.23,.10,0],[s*.23,.08,.18],.065);}
  sphere([0,1.77,0],.2,new THREE.MeshStandardMaterial({color:new THREE.Color(.8,.63,.43)}));
  sphere([0,1.77,.195],.055,new THREE.MeshStandardMaterial({color:new THREE.Color(.30,.22,.17)}));
  }
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(12,12),new THREE.MeshStandardMaterial({color:new THREE.Color(.72,.74,.77),side:THREE.DoubleSide}));floor.rotation.x=-Math.PI/2;scene.add(floor);
  if(config.floor_cues==='markers')for(const [x,z,c] of [[-.72,1.25,[.7,.25,.12]],[.72,1.25,[.2,.55,.3]],[-.72,-1.25,[.2,.3,.65]],[.72,-1.25,[.8,.6,.15]]]){
    const m=new THREE.Mesh(new THREE.PlaneGeometry(.4,.4),new THREE.MeshStandardMaterial({color:new THREE.Color(...c),side:THREE.DoubleSide}));m.rotation.x=-Math.PI/2;m.position.set(x,.008,z);scene.add(m);
  }
}
function rebuildScenes(){for(const [parent,group] of contentGroups){parent.remove(group);group.traverse(o=>{o.geometry?.dispose();if(o.material)o.material.dispose();});}contentGroups.length=0;buildScene(world);buildScene(clean);}
buildScene(world);buildScene(clean);
world.add(new THREE.GridHelper(12,12,0x8899aa,0x526478),new THREE.AxesHelper(2));
const editorCam=new THREE.PerspectiveCamera(45,1,.01,100);editorCam.position.set(7,6,8);
const camera=new THREE.PerspectiveCamera(45,config.width/config.height,.03,100);
const marker=new THREE.Mesh(new THREE.BoxGeometry(.24,.16,.3),new THREE.MeshBasicMaterial({color:0xffce6e}));world.add(marker);
const helper=new THREE.CameraHelper(camera);world.add(helper);
const wr=new THREE.WebGLRenderer({antialias:true}),pr=new THREE.WebGLRenderer({antialias:true});
wr.setPixelRatio(Math.min(devicePixelRatio,2));pr.setPixelRatio(Math.min(devicePixelRatio,2));
$('world').append(wr.domElement);$('preview').append(pr.domElement);
const orbit=new OrbitControls(editorCam,wr.domElement);orbit.target.set(0,1,0);orbit.update();
const transform=new TransformControls(editorCam,wr.domElement);transform.attach(marker);world.add(transform.getHelper());
transform.addEventListener('dragging-changed',e=>{orbit.enabled=!e.value;playing=false;});
transform.addEventListener('objectChange',()=>{
  if(updating)return;
  const p=marker.position.clone().sub(new THREE.Vector3(...pose.target));
  const distance=THREE.MathUtils.clamp(p.length(),.5,50);
  let angle=Math.atan2(p.x,p.z)*180/Math.PI;
  angle+=360*Math.round((pose.orbit-angle)/360);
  pose={...pose,distance,orbit:angle,elevation:THREE.MathUtils.clamp(Math.asin(THREE.MathUtils.clamp(p.y/(p.length()||1),-1,1))*180/Math.PI,-89.9,89.9)};
  changed();
});
let path;
function trajectory(){
  if(path){world.remove(path);path.geometry.dispose();path.material.dispose();}
  const points=[];const end=Math.max(state.keys.at(-1).t,.001);
  for(let i=0;i<=160;i++)points.push(new THREE.Vector3(...basis(sample(state,i*end/160)).position));
  path=new THREE.Line(new THREE.BufferGeometry().setFromPoints(points),new THREE.LineBasicMaterial({color:0x65f2d2}));world.add(path);
}
const specs=[['orbit','Orbit / 水平',-720,720,.1],['elevation','Elevation / 仰角',-89.9,89.9,.1],['distance','Distance / 距離',.5,50,.01],['fov','FOV / 画角',10,100,.1]];
for(const [name,label,min,max,step] of specs){
  const row=document.createElement('div');row.className='control';
  row.innerHTML=`<label for="${name}">${label}</label><input id="${name}" type="range" min="${min}" max="${max}" step="${step}"><input aria-label="${label} 数値" id="${name}Value" type="number" min="${min}" max="${max}" step="${step}">`;
  $('controls').append(row);
  for(const id of [name,name+'Value'])$(id).addEventListener('input',()=>{const v=Number($(id).value);if(!Number.isFinite(v))return;pose[name]=THREE.MathUtils.clamp(v,min,max);changed();});
}
for(const [i,id] of ['tx','ty','tz'].entries())$(id).onchange=()=>{const v=Number($(id).value);if(Number.isFinite(v)){pose.target[i]=THREE.MathUtils.clamp(v,-20,20);changed();}};
function changed(){playing=false;dirty=true;sync();$('status').textContent='未保存のカメラ位置 —「キー保存 / 更新」で軌道に反映します';}
function sync(){
  for(const [n] of specs){$(n).value=pose[n];$(n+'Value').value=Number(pose[n].toFixed(3));}
  ['tx','ty','tz'].forEach((id,i)=>$(id).value=Number(pose.target[i].toFixed(3)));
  $('time').value=Number(time.toFixed(3));$('timeline').value=time;
  $('play').textContent=playing?'❚❚ 一時停止':'▶ 再生';
  const b=basis(pose);camera.position.fromArray(b.position);camera.up.fromArray(b.up);camera.lookAt(...pose.target);camera.fov=pose.fov;camera.aspect=config.width/config.height;camera.updateProjectionMatrix();camera.updateMatrixWorld();
  updating=true;marker.position.copy(camera.position);marker.quaternion.copy(camera.quaternion);updating=false;helper.update();
}
function keysUI(){
  $('keys').replaceChildren();
  state.keys.forEach(k=>{const b=document.createElement('button');b.textContent=`◆ ${k.t.toFixed(3)}s`;b.classList.toggle('active',Math.abs(k.t-time)<.001);b.onclick=()=>seek(k.t);$('keys').append(b);});
  const end=(config.frames-1)/config.fps;$('timeline').max=end;$('time').max=end;
  $('duration').textContent=`/ ${end.toFixed(3)}秒 (${config.frames}f / ${config.fps}fps)`;
}
function emit(){parent.postMessage({type:'h3-camera-change',state},location.origin);trajectory();keysUI();}
function seek(t){playing=false;time=THREE.MathUtils.clamp(t,0,(config.frames-1)/config.fps);pose=sample(state,time);dirty=false;$('status').textContent='';sync();keysUI();}
$('timeline').oninput=()=>seek(Number($('timeline').value));$('time').onchange=()=>seek(Number($('time').value)||0);
$('add').onclick=()=>{const k=structuredClone(pose);k.t=Number(time.toFixed(6));const i=state.keys.findIndex(x=>Math.abs(x.t-k.t)<.001);if(i>=0)state.keys[i]=k;else if(state.keys.length<200)state.keys.push(k);else return;state.keys.sort((a,b)=>a.t-b.t);dirty=false;$('status').textContent='キーを保存しました';emit();};
$('delete').onclick=()=>{if(state.keys.length===1){$('status').textContent='キーを1つ以上残してください';return;}state.keys=state.keys.filter(k=>Math.abs(k.t-time)>=.001);emit();seek(time);};
$('preset').onclick=()=>{state=structuredClone(DEFAULT);const end=(config.frames-1)/config.fps;state.keys[1].t=Math.min(1,end/2);state.keys[2].t=end;if(end===0)state.keys=[state.keys[0]];emit();seek(0);};
$('play').onclick=()=>{if(dirty){$('status').textContent='再生前にキーを保存してください';return;}if(time>=(config.frames-1)/config.fps)time=0;playing=!playing;sync();};
$('stop').onclick=()=>seek(0);
function resize(){const a=$('world').getBoundingClientRect(),b=$('preview').getBoundingClientRect();if(a.width<1||a.height<1||b.width<1||b.height<1)return;wr.setSize(a.width,a.height,false);editorCam.aspect=a.width/a.height;editorCam.updateProjectionMatrix();pr.setSize(b.width,b.height,false);}
new ResizeObserver(resize).observe(document.body);
window.addEventListener('message',e=>{if(e.source!==parent||e.origin!==location.origin||e.data?.type!=='h3-camera-load')return;try{
  const incoming=e.data.state;if(incoming){if(incoming.version!==1||!Array.isArray(incoming.keys)||!incoming.keys.length)throw Error('Invalid state');state=structuredClone(incoming);state.keys.sort((a,b)=>a.t-b.t);}
  const previousShape=config.subject_shape,previousCues=config.floor_cues;
  config={...config,...e.data.config};if(previousShape!==config.subject_shape||previousCues!==config.floor_cues)rebuildScenes();trajectory();keysUI();seek(Math.min(time,(config.frames-1)/config.fps));
  const reuse=config.source_mode==='reuse_video';
  $('world').style.display=reuse?'none':'';$('preview').style.display=reuse?'none':'';
  document.querySelector('.panel').style.display=reuse?'none':'';
  resize();
  let notice=$('reuse-notice');if(!notice){notice=document.createElement('p');notice.id='reuse-notice';notice.style.cssText='padding:18px;line-height:1.8';document.body.append(notice);}
  notice.hidden=!reuse;notice.textContent='既存動画を再利用 / Reuse existing video — existing_video入力、またはvideo_pathの動画を出力します。キー・形状・width/height/frames/fpsは使用しません。元動画の寸法・フレーム数・fpsを保持します。H3には24fpsの動画を選んでください。プレビューは接続先のSave Videoで確認できます。';
}catch(err){$('status').textContent=`状態を読めません: ${err.message}`;}});
window.addEventListener('error',e=>$('status').textContent=e.message);
let last=performance.now();
function animate(now){const dt=Math.min((now-last)/1000,.1);last=now;if(config.source_mode==='reuse_video'){requestAnimationFrame(animate);return;}if(playing){time=Math.min(time+dt,(config.frames-1)/config.fps);pose=sample(state,time);if(time>=(config.frames-1)/config.fps)playing=false;sync();}wr.render(world,editorCam);
  // Letterbox preview to the exact export aspect ratio.
  const w=pr.domElement.clientWidth,h=pr.domElement.clientHeight,ratio=config.width/config.height;
  const vw=Math.min(w,h*ratio),vh=vw/ratio;pr.setScissorTest(false);pr.setClearColor(0x0b111b);pr.clear();pr.setViewport((w-vw)/2,(h-vh)/2,vw,vh);pr.setScissor((w-vw)/2,(h-vh)/2,vw,vh);pr.setScissorTest(true);pr.render(clean,camera);requestAnimationFrame(animate);
}
trajectory();keysUI();sync();resize();requestAnimationFrame(animate);parent.postMessage({type:'h3-camera-ready'},location.origin);
