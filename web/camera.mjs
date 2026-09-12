export const DEFAULT = {version:1, keys:[
  {t:0,orbit:0,elevation:85,distance:4,target:[0,1,0],fov:45},
  {t:1,orbit:0,elevation:0,distance:4,target:[0,1,0],fov:45},
  {t:5.125,orbit:90,elevation:0,distance:4,target:[0,1,0],fov:45}
]};
export function sample(state,t) {
  const keys=state.keys;
  if(t<=keys[0].t) return structuredClone(keys[0]);
  if(t>=keys.at(-1).t) return structuredClone(keys.at(-1));
  for(let i=1;i<keys.length;i++) {
    const a=keys[i-1],b=keys[i];
    if(t<=b.t) {
      let u=(t-a.t)/(b.t-a.t); u=u*u*(3-2*u);
      const k={t,target:a.target.map((v,j)=>v+(b.target[j]-v)*u)};
      for(const n of ['orbit','elevation','distance','fov']) k[n]=a[n]+(b[n]-a[n])*u;
      return k;
    }
  }
}
export function basis(k) {
  const a=k.orbit*Math.PI/180,e=k.elevation*Math.PI/180;
  const back=[Math.sin(a)*Math.cos(e),Math.sin(e),Math.cos(a)*Math.cos(e)];
  return {position:k.target.map((v,i)=>v+k.distance*back[i]),up:[-Math.sin(a)*Math.sin(e),Math.cos(e),-Math.cos(a)*Math.sin(e)]};
}
