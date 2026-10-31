import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import subprocess, shutil, threading, webbrowser
from datetime import datetime

BG="#0a0f1e"; PANEL="#111a2d"; CYAN="#56e3ee"; TEXT="#e7efff"; MUTED="#9aacca"

class FixaPro:
    def __init__(self, root):
        self.root=root; root.title("FixaPro Android Toolkit V4"); root.geometry("1100x720"); root.minsize(900,600); root.configure(bg=BG)
        self.mode=tk.StringVar(value="Not checked"); self.serial=tk.StringVar(value="—")
        self.model=tk.StringVar(value="—"); self.manufacturer=tk.StringVar(value="—"); self.android=tk.StringVar(value="—")
        self.frp=tk.StringVar(value="Not checked"); self._style(); self._header()
        self.tabs=ttk.Notebook(root); self.tabs.pack(fill="both",expand=True,padx=22,pady=10)
        self.overview=ttk.Frame(self.tabs,padding=15); self.adb=ttk.Frame(self.tabs,padding=15)
        self.reset=ttk.Frame(self.tabs,padding=15); self.fastboot=ttk.Frame(self.tabs,padding=15)
        self.frppage=ttk.Frame(self.tabs,padding=15); self.diag=ttk.Frame(self.tabs,padding=15); self.logpage=ttk.Frame(self.tabs,padding=10)
        for frame,title in [(self.overview,"Overview"),(self.adb,"ADB Tools"),(self.reset,"Factory Reset"),(self.fastboot,"Fastboot"),(self.frppage,"FRP Service"),(self.diag,"Diagnostics"),(self.logpage,"Activity Log")]:
            self.tabs.add(frame,text=title)
        self._overview(); self._adb(); self._reset(); self._fastboot(); self._frp(); self._diag(); self._logs()
        self.status=tk.StringVar(value="Ready")
        tk.Label(root,textvariable=self.status,bg="#0d1729",fg=MUTED,anchor="w",padx=22,pady=7).pack(fill="x",side="bottom")
        self.log("FixaPro Toolkit V4 started. Use only on devices you own or are authorized to service.")
        self.check_tools()

    def _style(self):
        s=ttk.Style()
        try:s.theme_use("clam")
        except:pass
        s.configure("TFrame",background=BG); s.configure("Panel.TFrame",background=PANEL)
        s.configure("TLabel",background=BG,foreground=TEXT,font=("Segoe UI",10))
        s.configure("Muted.TLabel",background=BG,foreground=MUTED,font=("Segoe UI",9))
        s.configure("Big.TLabel",background=BG,foreground=CYAN,font=("Segoe UI",21,"bold"))
        s.configure("PanelTitle.TLabel",background=PANEL,foreground=TEXT,font=("Segoe UI",12,"bold"))
        s.configure("TButton",padding=9,font=("Segoe UI",10,"bold"),background="#17233b",foreground=TEXT)
        s.map("TButton",background=[("active","#263958")])
        s.configure("Accent.TButton",background=CYAN,foreground="#07111d")
        s.configure("Danger.TButton",background="#762b40",foreground="white")
        s.configure("TNotebook",background=BG,borderwidth=0)
        s.configure("TNotebook.Tab",background="#17233b",foreground=TEXT,padding=(14,9))
        s.map("TNotebook.Tab",background=[("selected",CYAN)],foreground=[("selected","#07111d")])

    def _header(self):
        h=tk.Frame(self.root,bg=BG); h.pack(fill="x",padx=22,pady=(15,0))
        tk.Label(h,text="FixaPro",bg=BG,fg=CYAN,font=("Segoe UI",25,"bold")).pack(side="left")
        tk.Label(h,text="  ANDROID TOOLKIT  •  V4",bg=BG,fg=TEXT,font=("Segoe UI",13,"bold")).pack(side="left",pady=(10,0))
        ttk.Button(h,text="Export Report",command=self.export_report).pack(side="right",pady=8)

    def _title(self,parent,title,sub=""):
        ttk.Label(parent,text=title,style="Big.TLabel").pack(anchor="w")
        if sub: ttk.Label(parent,text=sub,style="Muted.TLabel").pack(anchor="w",pady=(3,14))

    def _card(self,parent,label,var,col):
        f=ttk.Frame(parent,style="Panel.TFrame",padding=12); ttk.Label(f,text=label,style="PanelTitle.TLabel").pack(anchor="w")
        tk.Label(f,textvariable=var,bg=PANEL,fg=CYAN,font=("Segoe UI",12,"bold"),wraplength=155,justify="left").pack(anchor="w",pady=(7,0))
        f.grid(row=0,column=col,sticky="nsew",padx=(0 if col==0 else 6,0)); parent.columnconfigure(col,weight=1)

    def _overview(self):
        self._title(self.overview,"Device Overview","Connection status and device identity")
        cards=ttk.Frame(self.overview); cards.pack(fill="x",pady=(0,14))
        for i,(label,var) in enumerate([("Mode",self.mode),("Serial",self.serial),("Manufacturer",self.manufacturer),("Model",self.model),("Android",self.android)]):self._card(cards,label,var,i)
        row=ttk.Frame(self.overview);row.pack(fill="x",pady=(0,14))
        ttk.Button(row,text="Detect ADB Device",style="Accent.TButton",command=lambda:self.run(["adb","devices","-l"],"adb")).pack(side="left",padx=(0,8))
        ttk.Button(row,text="Detect Fastboot",command=lambda:self.run(["fastboot","devices"],"fastboot")).pack(side="left",padx=8)
        ttk.Button(row,text="Read Device Details",command=self.read_details).pack(side="left",padx=8)
        box=ttk.Frame(self.overview,style="Panel.TFrame",padding=15);box.pack(fill="both",expand=True)
        ttk.Label(box,text="Important",style="PanelTitle.TLabel").pack(anchor="w")
        tk.Label(box,text="Factory reset may permanently erase local data. Resetting does NOT remove Google FRP; the previously synced Google account may still be required. This toolkit does not bypass FRP or remove account locks.",bg=PANEL,fg="#ffbdc6",justify="left",wraplength=900,font=("Segoe UI",10,"bold")).pack(anchor="w",pady=(10,0))

    def _adb(self):
        self._title(self.adb,"ADB Utilities","Requires USB debugging and authorization on the phone")
        grid=ttk.Frame(self.adb);grid.pack(fill="x")
        items=[("List Devices",["adb","devices","-l"]),("Read Device Details",None),("Reboot System",["adb","reboot"]),("Reboot Recovery",["adb","reboot","recovery"]),("Reboot Bootloader",["adb","reboot","bootloader"]),("Battery Status",["adb","shell","dumpsys","battery"]),("Storage Summary",["adb","shell","df","-h","/data"]),("USB Debug State",["adb","shell","settings","get","global","adb_enabled"])]
        for i,(label,cmd) in enumerate(items):
            cb=self.read_details if cmd is None else (lambda c=cmd:self.run(c))
            ttk.Button(grid,text=label,command=cb).grid(row=i//2,column=i%2,sticky="ew",padx=(0,10),pady=6)
        grid.columnconfigure(0,weight=1);grid.columnconfigure(1,weight=1)

    def _reset(self):
        self._title(self.reset,"Factory Reset","Recovery reset or explicit Fastboot wipe (device support varies)")
        warning=ttk.Frame(self.reset,style="Panel.TFrame",padding=15);warning.pack(fill="x",pady=(0,14))
        ttk.Label(warning,text="DATA LOSS WARNING",style="PanelTitle.TLabel").pack(anchor="w")
        tk.Label(warning,text="Back up data first and obtain the owner's consent. Reset can be irreversible. Confirm you know the Google account previously synced to this phone. Factory reset does not remove FRP.",bg=PANEL,fg="#ffbdc6",justify="left",wraplength=900,font=("Segoe UI",10,"bold")).pack(anchor="w",pady=(8,0))
        ttk.Button(self.reset,text="Reboot Connected Phone to Recovery",style="Accent.TButton",command=self.confirm_recovery).pack(anchor="w",pady=8)
        ttk.Button(self.reset,text="ADB Reset Option (Recovery Workflow)",command=self.confirm_adb_reset).pack(anchor="w",pady=8)
        ttk.Button(self.reset,text="Fastboot Factory Wipe (fastboot -w)",style="Danger.TButton",command=self.confirm_fastboot_wipe).pack(anchor="w",pady=8)
        box=ttk.Frame(self.reset,style="Panel.TFrame",padding=15);box.pack(fill="x",pady=12)
        ttk.Label(box,text="How this works",style="PanelTitle.TLabel").pack(anchor="w")
        tk.Label(box,text="Recovery buttons reboot an authorized ADB device to Recovery; select Wipe data/factory reset on the phone. Fastboot -w is available separately only when the device is already in Fastboot and the bootloader permits it. It erases user data and does NOT remove FRP. Availability and behavior vary by manufacturer/model.",bg=PANEL,fg=MUTED,justify="left",wraplength=900).pack(anchor="w",pady=(8,0))

    def _fastboot(self):
        self._title(self.fastboot,"Fastboot Utilities","Detection and basic information")
        row=ttk.Frame(self.fastboot);row.pack(fill="x")
        ttk.Button(row,text="Detect Fastboot Device",style="Accent.TButton",command=lambda:self.run(["fastboot","devices"],"fastboot")).pack(side="left",padx=(0,8))
        ttk.Button(row,text="Read Product",command=lambda:self.run(["fastboot","getvar","product"])).pack(side="left",padx=8)
        ttk.Button(row,text="Read Fastboot Info",command=lambda:self.run(["fastboot","getvar","all"])).pack(side="left",padx=8)
        ttk.Button(row,text="Reboot Device",command=lambda:self.run(["fastboot","reboot"])).pack(side="left",padx=8)
        ttk.Label(self.fastboot,text="Unlock, flash and arbitrary erase commands are not included. Factory wipe is available in the Factory Reset tab with extra confirmation.",style="Muted.TLabel").pack(anchor="w",pady=20)

    def _frp(self):
        self._title(self.frppage,"FRP Status & Authorized Service","Model details and legitimate account recovery workflow")
        box=ttk.Frame(self.frppage,style="Panel.TFrame",padding=15);box.pack(fill="x",pady=(0,12))
        ttk.Label(box,text="FRP Status",style="PanelTitle.TLabel").pack(anchor="w")
        tk.Label(box,textvariable=self.frp,bg=PANEL,fg=CYAN,font=("Segoe UI",11,"bold"),wraplength=850,justify="left").pack(anchor="w",pady=8)
        ttk.Button(box,text="Read Available Model Details",style="Accent.TButton",command=self.check_frp_details).pack(anchor="w")
        guide=ttk.Frame(self.frppage,style="Panel.TFrame",padding=15);guide.pack(fill="both",expand=True)
        ttk.Label(guide,text="Authorized Service Workflow",style="PanelTitle.TLabel").pack(anchor="w")
        text=("1. Confirm ownership and customer consent; record model and relevant service details.\n"
              "2. Explain that a reset can trigger Google FRP and the previously synced account may be required.\n"
              "3. Help the owner recover the Google account through the official recovery page.\n"
              "4. If recovery is unavailable, refer the owner to the manufacturer's authorized support with proof of ownership.\n"
              "5. Do not collect or store customer passwords in this application.\n\n"
              "FRP state cannot be reliably confirmed through one universal ADB command. This page reports available model details; it does not claim a definitive FRP detection result.")
        tk.Label(guide,text=text,bg=PANEL,fg=MUTED,justify="left",anchor="nw",wraplength=900,font=("Segoe UI",10)).pack(fill="both",expand=True,pady=(10,12))
        ttk.Button(guide,text="Open Google Account Recovery",command=lambda:webbrowser.open("https://accounts.google.com/signin/recovery")).pack(anchor="w",pady=(0,8))
        ttk.Button(guide,text="Google Android Help: Factory reset & account",command=lambda:webbrowser.open("https://support.google.com/android/answer/6088915" )).pack(anchor="w")

    def _diag(self):
        self._title(self.diag,"PC Diagnostics","Check ADB and Fastboot setup")
        row=ttk.Frame(self.diag);row.pack(fill="x")
        ttk.Button(row,text="Check Both",style="Accent.TButton",command=self.check_tools).pack(side="left",padx=(0,8))
        ttk.Button(row,text="Official Platform Tools",command=lambda:webbrowser.open("https://developer.android.com/tools/releases/platform-tools")).pack(side="left",padx=8)
        self.diagtext=tk.Text(self.diag,bg="#080d18",fg="#bde8f4",insertbackground="white",relief="flat",font=("Consolas",10),padx=12,pady=12)
        self.diagtext.pack(fill="both",expand=True,pady=(14,0))

    def _logs(self):
        self.logtext=tk.Text(self.logpage,bg="#080d18",fg="#d7e4ff",insertbackground="white",relief="flat",font=("Consolas",9),padx=12,pady=12)
        self.logtext.pack(fill="both",expand=True)
        row=ttk.Frame(self.logpage);row.pack(fill="x",pady=(8,0))
        ttk.Button(row,text="Save Log",command=self.save_log).pack(side="right")
        ttk.Button(row,text="Clear Log",command=lambda:self.logtext.delete("1.0","end")).pack(side="right",padx=8)

    def log(self,msg):
        if hasattr(self,"logtext"):
            self.logtext.insert("end",f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n");self.logtext.see("end")

    def check_tools(self):
        lines=[]
        for t in ("adb","fastboot"):
            p=shutil.which(t);lines.append(f"{t}: {'FOUND at '+p if p else 'NOT FOUND — install Android Platform Tools and add folder to PATH'}")
        self.diagtext.delete("1.0","end");self.diagtext.insert("end","\n".join(lines)+"\n")
        self.status.set(" | ".join(f"{t}: {'OK' if shutil.which(t) else 'Missing'}" for t in ("adb","fastboot")))
        for line in lines:self.log(line)

    def run(self,cmd,target="log"):
        self.log("Running: "+" ".join(cmd));self.status.set("Running command…")
        threading.Thread(target=self._worker,args=(cmd,target),daemon=True).start()

    def _worker(self,cmd,target):
        try:
            p=subprocess.run(cmd,capture_output=True,text=True,timeout=35,shell=False)
            out="\n".join(x.strip() for x in (p.stdout,p.stderr) if x and x.strip()) or f"Command completed (exit {p.returncode})."
            self.root.after(0,lambda:self._result(cmd,out,p.returncode,target))
        except FileNotFoundError:
            self.root.after(0,lambda:self._result(cmd,f"{cmd[0]} not found. Install Android Platform Tools and configure PATH.",127,target))
        except Exception as e:
            msg=str(e);self.root.after(0,lambda:self._result(cmd,msg,1,target))

    def _result(self,cmd,out,code,target):
        self.status.set(f"Finished (exit {code})");self.log(f"Exit {code}: {' '.join(cmd)}");self.log(out.replace("\n"," | "))
        if target=="adb":self._parse_adb(out)
        if target=="fastboot":
            self.mode.set("Fastboot detected" if out.strip() else "No Fastboot device")
            self.serial.set(out.split()[0] if out.strip() else "—")
        self.tabs.select(self.logpage)

    def _parse_adb(self,out):
        found=[]
        for line in out.splitlines():
            p=line.split()
            if len(p)>=2 and p[1] in ("device","unauthorized","offline"):found.append((p[0],p[1]))
        if not found:
            self.mode.set("No ADB device");self.serial.set("—");self.model.set("—");self.manufacturer.set("—");self.android.set("—")
            self.log("No ADB device detected.");return
        self.serial.set(found[0][0]);self.mode.set("ADB: "+found[0][1])
        if found[0][1]=="device":self.read_details()

    def read_details(self):
        if not shutil.which("adb"):
            messagebox.showwarning("ADB not found","Install Android Platform Tools and configure PATH first.");return
        props=[("Model",["adb","shell","getprop","ro.product.model"]),("Manufacturer",["adb","shell","getprop","ro.product.manufacturer"]),("Android",["adb","shell","getprop","ro.build.version.release"]),("Build",["adb","shell","getprop","ro.build.display.id"]),("Security patch",["adb","shell","getprop","ro.build.version.security_patch"]),("Serial",["adb","get-serialno"])]
        def work():
            vals={}
            for label,cmd in props:
                try:
                    p=subprocess.run(cmd,capture_output=True,text=True,timeout=12,shell=False);vals[label]=(p.stdout or p.stderr).strip()
                except Exception as e:vals[label]=str(e)
            self.root.after(0,lambda:self._show_details(vals))
        threading.Thread(target=work,daemon=True).start();self.log("Reading device properties…")

    def _show_details(self,v):
        self.model.set(v.get("Model") or "—");self.manufacturer.set(v.get("Manufacturer") or "—");self.android.set(v.get("Android") or "—");self.mode.set("ADB connected")
        self.diagtext.delete("1.0","end");self.diagtext.insert("end","FixaPro Device Report\n"+"="*30+"\n"+"\n".join(f"{k}: {val or '(not available)'}" for k,val in v.items()))
        self.log("Device properties loaded.");self.tabs.select(self.overview)

    def confirm_recovery(self):
        if messagebox.askyesno("Confirm Reboot","Reboot the connected authorized ADB phone into Recovery? This does not itself erase data."):
            self.run(["adb","reboot","recovery"])

    def confirm_adb_reset(self):
        messagebox.showwarning("Factory Reset Safety","This option uses ADB only to reboot into Recovery. It does not automatically erase data. Use the phone manufacturer's on-device recovery reset menu. FRP may still require the previously synced Google account.")
        if messagebox.askyesno("Reboot to Recovery","Continue and reboot the connected ADB device to Recovery?"):
            self.run(["adb","reboot","recovery"])

    def confirm_fastboot_wipe(self):
        if not shutil.which("fastboot"):
            messagebox.showwarning("Fastboot not found","Android Platform Tools are required."); return
        if not messagebox.askyesno("PERMANENT DATA WIPE", "This runs fastboot -w on the connected Fastboot device. It can permanently erase user data. FRP/Google account verification may still be required after reset. Continue only with owner consent and a backup."):
            return
        phrase=simpledialog.askstring("Confirm wipe", "Type WIPE to confirm fastboot -w:")
        if phrase != "WIPE":
            messagebox.showinfo("Cancelled", "Wipe cancelled; no command was run."); return
        self.run(["fastboot","-w"],"fastboot")

    def check_frp_details(self):
        self.frp.set("FRP state cannot be confirmed universally by this app. Reading available model details…")
        if not shutil.which("adb"):
            self.frp.set("ADB not available. Install Platform Tools and connect an authorized phone.");return
        self.read_details()
        self.log("FRP status is not directly detected; use authorized account recovery workflow.")

    def export_report(self):
        report=f"FixaPro Android Toolkit V4\nGenerated: {datetime.now().isoformat(timespec='seconds')}\nMode: {self.mode.get()}\nSerial: {self.serial.get()}\nManufacturer: {self.manufacturer.get()}\nModel: {self.model.get()}\nAndroid: {self.android.get()}\n\nFRP: {self.frp.get()}\n\n"
        if hasattr(self,"diagtext"):report+=self.diagtext.get("1.0","end")
        path=filedialog.asksaveasfilename(defaultextension=".txt",filetypes=[("Text report","*.txt")],initialfile="FixaPro_Service_Report.txt")
        if path:
            with open(path,"w",encoding="utf-8") as f:f.write(report)
            messagebox.showinfo("Export complete","Report saved.");self.log("Report exported: "+path)

    def save_log(self):
        path=filedialog.asksaveasfilename(defaultextension=".txt",filetypes=[("Text log","*.txt")],initialfile="FixaPro_Activity_Log.txt")
        if path:
            with open(path,"w",encoding="utf-8") as f:f.write(self.logtext.get("1.0","end"))
            messagebox.showinfo("Saved","Activity log saved.")

def main():
    root=tk.Tk();FixaPro(root);root.mainloop()
if __name__=="__main__":main()
