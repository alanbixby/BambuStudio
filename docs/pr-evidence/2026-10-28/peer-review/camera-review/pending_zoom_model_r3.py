# Round-three model of DeviceWebHost::ApplyAmsControlWebHostSize / SetAmsControlWebFitZoom
# @df28193c and StatusBasePanel::fit_camera_to_feed (unchanged since 6e81cd8f), with the
# same panel-height assumptions as the round-two model. Only structural behaviour is claimed.
#
# Host state machine follows the source line by line:
#   SetAmsControlWebFitZoom: early return if |dz|<0.001; fz=z; last_reported=None;
#       h = last_logical_h if >0 else 340 (kAmsControlWebInitialHeightDip); Apply(h)
#   Apply(h): clamp [220,360]; last_logical_h=h; content=(lround(D(586)*fz), lround(D(h)*fz));
#       zoom API only when view && native backend (not on OSX); jitter/equality returns;
#       SetMinSize on panel via handler -> size event -> CallAfter(fit)
#   wgtAmsControlWebPanel::GetBaseHeight = lround(min_h / m_fit_zoom)
import math, itertools, sys

def lround(x): return int(math.floor(x + 0.5)) if x >= 0 else -int(math.floor(-x + 0.5))

class Host:
    def __init__(self, s, panel, ready, old_head=False):
        self.s=s; self.panel=panel; self.ready=ready; self.old_head=old_head
        self.fz=1.0; self.base_zoom=0.0; self.last_logical_h=-1; self.last_reported=None
        self.view_zoom=1.0; self.api_calls=0; self.api_calls_unready=0; self.set_zoom_values=[]
        self.size_events=0
    def D(self,d): return lround(d*self.s)
    def apply(self,h):
        h=min(max(h,220),360)
        self.last_logical_h=h
        content=(lround(self.D(586)*self.fz), lround(self.D(h)*self.fz))
        if self.ready():
            if self.base_zoom<=0: self.base_zoom=self.view_zoom; self.api_calls+=1
            z=self.base_zoom*self.fz
            self.api_calls+=1
            if abs(self.view_zoom-z)>0.001: self.view_zoom=z; self.api_calls+=1; self.set_zoom_values.append(round(z,3))
        else:
            pass  # gate skips all zoom API calls
        if self.last_reported is not None:
            dh=content[1]-self.last_reported[1]; J=self.D(8)
            if -J<dh<J: return
        if content==self.last_reported: return
        self.last_reported=content
        self.panel.min=content
        self.size_events+=1   # handler -> Layout/SendSizeEvent -> CallAfter(fit)
    def set_fit_zoom(self,z):
        if abs(z-self.fz)<0.001: return
        self.fz=z
        if self.old_head:   # 6e81cd8f: return before resizing when no report yet
            if self.last_logical_h<=0: return
            self.last_reported=None; self.apply(self.last_logical_h); return
        self.last_reported=None
        self.apply(self.last_logical_h if self.last_logical_h>0 else 340)
    def report(self,h): self.apply(h)

class Panel:
    def __init__(self,s): self.s=s; self.min=(lround(586*s), lround(340*s)); self.fz=1.0; self.host=None
    def set_fit_zoom(self,z): self.fz=z; self.host.set_fit_zoom(z)
    def base_h(self): return lround(self.min[1]/self.fz)
    def base_w(self): return lround(586*self.s)

def make_fit(s):
    D=lambda d: lround(d*s)
    title, play, media_min, cam_min_w, sep = D(36), D(40), D(288), D(574), D(10)
    bw, border = D(586), D(16)
    T=lround(240*s/1.5)
    rows_other = lround((8*1.5+330+6*1.5+6*1.5+90+4*1.5)*s/1.5)
    C0 = title + rows_other
    natural = lround(921*s/1.5)
    rows_base = bw + border
    extra_w = natural - rows_base + border
    chrome = title + play
    def step(z): return min(max(math.floor(z*20+1e-6)/20, 1.0), 2.0)
    def fit(W, V, aspect, panel):
        B = panel.base_h(); min_h = panel.min[1]; z_cur = panel.fz
        M = title + media_min + play + sep + T
        Hc = C0 + min_h
        R = max(V, Hc, M)
        camera_h = R - M + media_min
        extra_h = C0
        level = (W - extra_w + aspect*(chrome - extra_h))/(bw + aspect*B)
        tallest = (chrome + camera_h - extra_h)/B
        f = min(level, tallest); z = step(f)
        control_w = max(natural, math.ceil(z*bw) + extra_w)
        feed_h = camera_h
        if f < 2: feed_h = min(camera_h, extra_h + z*B - chrome)
        feed_w = max(cam_min_w, min(math.ceil(feed_h*aspect), W - control_w))
        target = W - feed_w if W - feed_w > natural else None
        z = min(z, step(((target if target else natural) - extra_w)/bw))
        changed = abs(z_cur - z) > 0.001
        if changed: panel.set_fit_zoom(z)
        return z, changed
    return fit

def run(s, W, V, page_h, ready_after, old_head=False, aspect=16/9, wide_first=None, max_passes=8):
    panel=Panel(s); state={'n':0}
    def ready(): return state['n']>=ready_after
    host=Host(s,panel,ready,old_head); panel.host=host
    fit=make_fit(s)
    pre=[]  # zoom after each pre-report pass
    for i in range(max_passes):
        z,ch=fit(W,V,aspect,panel); pre.append(z)
        if not ch: break
    pre_changes=len(set(pre))-1 if pre else 0
    base_pre=[panel.base_h()]
    unready_api=host.api_calls  # must be 0 while unready
    state['n']=ready_after      # backend becomes ready (no-op for GTK)
    post=[]
    if wide_first is not None:  # Edge: page first lays out in the pre-widened host at zoom 1
        host.report(wide_first)
        for i in range(max_passes):
            z,ch=fit(W,V,aspect,panel); post.append(z)
            if not ch: break
    host.report(page_h)
    for i in range(max_passes):
        z,ch=fit(W,V,aspect,panel); post.append(z)
        if not ch: break
    # reference: report first, then fit to steady state
    rp=Panel(s); rs={'n':1}; rh=Host(s,rp,lambda: True); rp.host=rh; rf=make_fit(s); rh.report(page_h)
    ref=[]
    for i in range(max_passes):
        z,ch=rf(W,V,aspect,rp); ref.append(z)
        if not ch: break
    return dict(pre=pre, pre_distinct=len(set(pre)), unready_api=unready_api, post=post,
                final=post[-1] if post else pre[-1], ref=ref[-1], set_zooms=host.set_zoom_values,
                base_h_pre=panel.base_h, min_pre=panel.min)

def main():
    worst_pre=0; mismatches=[]; flashes=0; cases=0
    scen=[(6792,1581,"wide"),(2215,1240,"2560x1440@150"),(1900,1100,"modest"),(2560,900,"ultrawide-short")]
    for s in (1.0,1.5,2.0):
        for (W,V,label) in scen:
            Ws=lround(W*s/1.5); Vs=lround(V*s/1.5)
            for page_h in (220,260,300,336,340,344,360):
                for ready_after in (0,3):
                    r=run(s,Ws,Vs,page_h,ready_after)
                    cases+=1
                    worst_pre=max(worst_pre,r['pre_distinct'])
                    assert r['unready_api']==0 if ready_after>0 else True
                    if abs(r['final']-r['ref'])>1e-9: mismatches.append((s,label,page_h,ready_after,r))
                    # zoom changes after the first report beyond the reference's own settling
                    extra=len(set(r['post']))-1 - (len(set(r['ref'] if False else [0]))-1)
                    if extra>1: flashes+=1
    print(f"cases={cases} max distinct zoom values across pre-report passes={worst_pre} (1 means no drift)")
    print(f"final-vs-reference mismatches={len(mismatches)}; cases with >1 post-report zoom change={flashes}")
    for m in mismatches[:5]: print("  mismatch", m)
    print()
    print("== detail: 144 DPI wide, page 220, GTK-ready")
    r=run(1.5,6792,1581,220,0); print(" pre:",r['pre']," post:",r['post']," ref:",r['ref']," SetZoomFactor values:",r['set_zooms'])
    print("== detail: 144 DPI wide, page 340, Edge ready after 3 passes, page first reports wide-layout 260")
    r=run(1.5,6792,1581,340,3,wide_first=260); print(" pre:",r['pre']," unready API calls:",r['unready_api']," post:",r['post']," ref:",r['ref']," SetZoomFactor values:",r['set_zooms'])
    print("== detail: 96 DPI 2560x1440@150-class, page 300, GTK")
    r=run(1.0,lround(2215/1.5),lround(1240/1.5),300,0); print(" pre:",r['pre']," post:",r['post']," ref:",r['ref'])
    print("== contrast: old head 6e81cd8f (deferred pre-report), 144 DPI wide, page 340")
    r=run(1.5,6792,1581,340,0,old_head=True); print(" pre:",r['pre']," post:",r['post']," ref:",r['ref']," SetZoomFactor values:",r['set_zooms'])
    print("== GetBaseHeight round trip exactness over zoom steps and DPI")
    bad=[(s,z) for s in (1.0,1.25,1.5,1.75,2.0) for z in [1+0.05*k for k in range(21)] if lround(lround(lround(340*s)*z)/z)!=lround(340*s)]
    print(" failures:",bad)
main()
