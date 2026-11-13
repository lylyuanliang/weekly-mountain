# 璋冩煡涓庝慨澶嶏細绉诲姩绔墦寮€鍙嶉寮圭獥闂儊闂 (Fix Agent Feedback Modal Open Flash)

> **璐熻矗浜?*锛欰ntigravity Agent
> **寮€濮嬫椂闂?*锛?026-11-13
> **鍙嶉缂栧彿**锛?1794538942042
> **鐘舵€?*锛氬凡瑙ｅ喅 (Resolved)

---

## 1. 鐩爣涓庤儗鏅?鐢ㄦ埛鍦ㄧЩ鍔ㄧ鐪熸満锛堝皬绫?15 / Android 16 / Snapdragon 8 Elite / Chromium 156 WebView锛夌偣鍑诲彸渚ц兌鍥?`[路 鍙嶉缁?AI]` 鎵撳紑鍙嶉寮圭獥鏃讹紝鐣岄潰鍙戠敓浜嗕竴娆℃槑鏄剧獊鍏€鐨勯棯鐑侊紙Flash锛夈€?鐢ㄦ埛鎻愬嚭鏄庣‘璇夋眰锛?> "鎵撳紑鍙嶉杩樻槸浼氶棯涓€涓嬶紝鍒嗘瀽鏄摢閲岀殑闂锛屽鏋滄槸agent-feedback鐨勯棶棰橈紝瑕佸強鏃惰窡鎴戣"

---

## 2. 甯х骇鍒帓鏌ヨ建杩?(Frame-by-Frame Trace)
浠庣湡鏈哄綍灞?`scratch/feedback/media/1794538878966_1000018465.mp4` 鎸?25ms 绮惧害鎻愬彇搴忓垪甯э紙`scratch/flash_frames_step/`锛夛細
1. **700ms - 725ms (`f_00` - `f_01`)**锛氱敤鎴锋墜鎸囪交瑙︾偣鍑昏兌鍥婃寜閽?`[路 鍙嶉缁?AI]`銆?2. **750ms - 775ms (`f_02_750ms.png`, 77KB)**锛?*绗竴娆＄櫧灞?榛戝睆闂儊** 鈥斺€?鍏ㄥ睆鑳屾櫙鐩存帴鍙橀粦骞堕珮鏂ā绯婏紙75% 榛?+ 8px 妯＄硦锛夛紝浣嗗脊绐楀崱鐗囨湰浣撳畬鍏ㄤ笉瀛樺湪锛坄opacity: 0`锛夈€?3. **800ms - 925ms (`f_04` - `f_09`)**锛氬脊绐楁贰鍏ワ紝鍗＄墖涓讳綋鏄剧ず銆?4. **950ms - 975ms (`f_10_950ms.png`, 190KB)**锛?*绗簩娆′弗閲嶉€忔槑闂儊** 鈥斺€?寮圭獥搴曟澘鑳屾櫙锛坄#161922`锛夈€侀《閮ㄦ爣棰樻爮涓庡崱鐗囪竟妗嗙灛闂存秷澶?鍙橀€忔槑锛岀洿鎺ラ€忓嚭涓嬫柟妯＄硦鐨勬鑹插叕璺湴鍥撅紱浠呮湁鍏峰鐙珛婊氬姩/鏃嬭浆灞傜殑 Tab 鏍忓拰 `妫€娴嬪紑鍙戞満浜х墿涓?..` 鎸夐挳鎮┖娴湪鍦板浘涓婏紒
5. **1000ms (`f_12_1000ms.png`)**锛氬脊绐楀簳鏉块噸鏂扮粯鍒跺洖鏉ャ€?
---

## 3. 鏍瑰洜娣卞害鍓栨瀽 (Root Cause Analysis)

### 鏄笉鏄?`@lylyuanliang/agent-feedback` 鐨勯棶棰橈紵
**缁撹锛氭槸鏍稿績涓诲洜锛?* 涓昏闆嗕腑鍦ㄤ互涓嬩笁涓簳灞傛満鍒剁己闄凤細

1. **`toggleModal` 鍏ㄩ噺閿€姣佸苟閲嶅缓 Shadow DOM锛圖OM Wiping Flash锛?*锛?   - 姣忔璋冪敤 `toggleModal(true)` 鎴?`toggleModal(false)` 鏃讹紝搴曞眰鐩存帴鎵ц浜?`this.render(); this.bindEvents();`锛屽叏閲忛噸鍐?`this.shadow.innerHTML`锛?   - 瀵艰嚧鎵€鏈夊唴鑱?`<style>` 鏍囩琚祻瑙堝櫒閲嶆柊瑙ｆ瀽锛屾墍鏈?DOM 鑺傜偣琚攢姣侀噸寤猴紝鐢熷懡鍛ㄦ湡琚噸缃紝寮曞彂棣栧抚涓㈠抚銆?2. **閬僵灞傛棤娓愬彉鍔ㄧ敾涓庡脊绐楁贰鍏ユ椂闂村樊锛圔ackdrop Asynchrony Flash锛?*锛?   - `.modal-backdrop` 閲囩敤 `display: ${this.isOpen ? 'flex' : 'none'};`锛屽湪鎵撳紑鐬棿浠?0ms 閫熷害鏆村姏閾烘弧 75% 榛戣壊涓?8px 妯＄硦锛?   - 鑰?`.modal-container` 鐨?`@keyframes modal-pop` 浠?`opacity: 0` 寮€濮嬫墽琛?0.2s 鍔ㄧ敾銆?   - 瀵艰嚧鍓?50ms 灞忓箷鍙嚭鐜版殫榛戞ā绯婅挋灞傝€屾病鏈夊脊绐椾富浣擄紙鍗?750ms 澶勭殑绌哄眰闂儊锛夈€?3. **Chromium 纭欢鍔犻€熷悎鎴愬眰娉ㄩ攢鏃剁殑绾圭悊涓㈠純锛圕omposited Layer De-compositing Flash锛?*锛?   - `.modal-container` 澹版槑浜?`animation: modal-pop 0.2s cubic-bezier(0.16, 1, 0.3, 1);`锛屼絾**缂哄皯 `both` / `forwards`**锛屼笖**鏈０鏄庢寔缁殑纭欢鍔犻€?*锛堢己灏?`transform: translateZ(0)` / `will-change: transform`锛夛紱
   - 鍔ㄧ敾鍦ㄦ伆濂?200ms锛堝嵆瑙嗛 750ms + 200ms = 950ms锛夌粨鏉熸椂锛孋hromium 璁ゅ畾璇ュ厓绱犲凡鏃犳椿璺冨姩鐢伙紝绔嬪嵆**閿€姣佽 GPU 鍚堟垚鍥惧眰锛圙raphicsLayer锛?*骞跺皢鍏跺洖閫€鍚堝苟鑷充富灞傦紱
   - 鍦ㄥ畨鍗?WebView锛堝挨鍏堕珮鍒嗗睆 DPR 3.25 涓嬶級鍥為€€鍚堝苟骞堕噸鏂板厜鏍呭寲锛圧e-rasterize锛夋椂锛岃儗鏅汗鐞嗕骇鐢?1-2 甯х殑涓㈠け锛?   - 涓庢鍚屾椂锛宍.tabs`锛堝惈鏈?`-webkit-overflow-scrolling: touch`锛夊拰姝ｅ湪鏃嬭浆鐨?`.spinner` 鎷ユ湁鐙珛鐨勬粴鍔?鍔ㄧ敾鍚堟垚灞傦紝骞舵湭琚敞閿€锛屽洜鑰屽嚭鐜颁簡 950ms 鏃垛€滃簳鏉夸笌鏍囬娑堝け銆乀ab 涓?Spinner 鎮┖閫忓嚭鍦板浘鈥濈殑鍏稿瀷鍥惧眰鑴辫妭鐜拌薄锛?
### 涓氬姟绔紙`weekly-mountain`锛夌殑浼寸敓娆″洜
1. `alpineDevApkPlugin.js` 鍘熷厛鍦?`render()` 涓娇鐢ㄤ簡 `await Promise.all([import('vue'), import(...)])` 寮傛鍔ㄦ€佸姞杞斤紝鍦ㄥ脊绐楀垰鎵撳紑鏃跺鍣ㄤ负绌猴紝浜х敓浜屾甯冨眬璺冲姩锛?2. `.spinner` 鏃嬭浆鍔ㄧ敾缂哄皯 `transform: translateZ(0)`锛屼笌鐖跺浘灞備骇鐢熷鍚堥噸缁樼珵浜夈€?
---

## 4. 淇涓庝紭鍖栬惤鍦版竻鍗?
### 涓€銆乣@lylyuanliang/agent-feedback-client`锛堝簳灞?SDK 淇锛?鏂囦欢浣嶇疆锛歚D:\file_save\workspace\github\agent-feedback\packages\client\src\index.ts`
1. **瀹炵幇鍘熺敓灞€閮?`toggleModalDom` 闆堕噸鏋勬満鍒?*锛?   - `toggleModal(open)` 缁濅笉鍐嶈皟鐢?`this.render()` 閲嶅啓 `innerHTML`锛屾敼涓烘搷浣?`.modal-backdrop` 鐨?`.af-modal-open` 绫诲悕锛?   - 寮圭獥灞曞紑鏃讹紝淇濈暀鎵€鏈夊凡鎸傝浇鐨勫瓙缁勪欢銆丏OM 缁撴瀯銆佺敤鎴疯緭鍏ヤ笌婊氬姩浣嶇疆锛屽疄鐜?0ms 鏋侀€熷搷搴旓紱
2. **纭欢鍔犻€熶笌骞虫粦杩囨浮缁熶竴**锛?   - `.modal-backdrop` 澧炲姞 `opacity: 0` 鉃?`opacity: 1` 鐨?0.2s 骞虫粦 transition锛屾秷闄ょ灛闂撮粦灞忥紱
   - `.modal-container` 澧炲姞 `will-change: transform, opacity;`銆乣transform: translateZ(0);` 浠ュ強 `-webkit-backface-visibility: hidden;`锛屽苟缁欏姩鐢绘坊鍔?`both`锛坄animation: modal-pop 0.2s cubic-bezier(...) both`锛夛紱
   - 姘镐箙閿氬畾 GPU 鐙珛鍥惧眰锛屽交搴曟秷闄?200ms 鍔ㄧ敾缁撴潫鏃?Chromium 娉ㄩ攢鍥惧眰瀵艰嚧鐨勫簳鏉胯儗鏅棯鐑佷涪甯э紱
3. **瀹夊叏涓庡悗鍙伴潤榛橀槻鎶?*锛?   - `setAccessControl` 涓?`setHostChannel` 澧炲姞闂ㄧ淇濇姢锛屽脊绐楀浜庢墦寮€鐘舵€佹椂缁濅笉鏆村姏瑙﹀彂 `render()` 鎵撴柇鐢ㄦ埛鎿嶄綔锛?   - `openFeedbackModal(tab)` 浼樺厛璁剧疆 `setTab(tab)` 鍚庡啀鍛煎嚭妯℃€佹锛屾潨缁濇墦寮€杩囩▼涓殑浜屾 Tab 鍒囨崲鎶栧姩锛?4. **缂栬瘧涓庡悓姝?*锛?   - 鎵ц `pnpm run build` 閫氳繃 `tsc` 缂栬瘧鍑烘柊鐗?`dist/`锛?   - 杩愯 29 椤瑰崟鍏冩祴璇曞叏閮ㄩ€氳繃锛?9/29 Pass锛夛紱
   - 鐗╃悊鍚屾缂栬瘧浜х墿鑷?`weekly-mountain/node_modules/@lylyuanliang/agent-feedback-client/dist/`銆?
### 浜屻€乣weekly-mountain`锛堜笟鍔＄浼寸敓璋冧紭锛?1. `src/debug/alpineDevApkPlugin.js`锛?   - 鏀逛负鍚屾蹇€熸寕杞斤紝娑堥櫎 `Promise.all` 鍔ㄦ€佸姞杞藉甫鏉ョ殑棣栧抚甯冨眬绌哄眰锛?2. `src/components/debug/AlpineDevApkExtensionView.vue`锛?   - 涓?`.spinner` 鏄惧紡娣诲姞 `will-change: transform; transform: translateZ(0);`锛岄殧绂绘棆杞浘灞傦紝鏉滅粷瑙﹀彂閲嶇粯銆?
---

## 5. 鎭㈠鏈湴璋冭瘯鍖呭簲鐢ㄥ唴涓嬭浇涓庢柇鐐圭画浼犲姛鑳?(Restore In-App Resumable Download)

### 5.1 鏋舵瀯涓庢ā鍧楀綊灞炵晫瀹?鏍规嵁鐢ㄦ埛鎸囩ず锛氣€滀笅杞芥湰鍦拌皟璇曞寘鐨勬椂鍊欙紝鏃╂湡鐗堟湰鏄敮鎸佸簲鐢ㄥ唴涓嬭浇浠ュ強鏀寔鏂偣缁紶鐨勶紝鐜板湪鏄烦杞祻瑙堝櫒涓嬭浇锛宎gent-feedback鐨勮繖涓姛鑳戒篃鎭㈠涓€涓嬪憿锛堝簲璇ユ槸淇敼鍏蜂綋鐨勬彃浠舵ā鍧楀惂锛燂級鈥濄€?缁忕郴缁熸灦鏋勬帓鏌ワ紝璇ヨ兘鍔涚殑妯″潡鍒嗗竷濡備笅锛?1. **閫氱敤 SDK 灞傦紙`@lylyuanliang/agent-feedback-client`锛?*锛氫繚鎸佽交閲忕函鍑€涓庨€氱敤鎬э紝璐熻矗鎵胯浇瀹夸富閫氫俊銆佹巿鏉冩牎楠屼笌鎻掍欢鎵╁睍 Tab 鎸傝浇鐐癸紙`registerExtensionTab`锛夛紱
2. **涓氬姟鎻掍欢灞傦紙`src/components/debug/AlpineDevApkExtensionView.vue`锛?*锛氭鏄敤鎴锋墍鎸囩殑鈥滃叿浣撴彃浠舵ā鍧椻€濓紙鍗斥€滒煋?鏈湴鍖呪€濆紑鍙戣€呮墿灞曢潰鏉匡級銆傛鍓嶅彈缃戠粶绌块€忛噸鏋勫奖鍝嶏紝闄嶇骇涓轰簡澶栭儴娴忚鍣ㄥ敜璧凤紱鏈宸插叏閲忔仮澶嶄笌鍘熺敓瀹夸富妗ユ帴鐨勬繁搴﹁仈鍔紱
3. **鍘熺敓瀹夸富灞傦紙`android/app/src/main/java/.../MainActivity.java`锛?*锛氬師鐢熷凡鍏峰瀹屾暣鐨?HTTP 206 `Range: bytes=existingLength-` 鏂偣缁紶寮曟搸锛屽唴缃?`WakeLock` & `WifiLock` 閿侀槻姝㈠垏灞忕潯鐪狅紝骞堕€氳繃 `window.onAlpineDownloadProgress(data)` 鍚戝墠绔?WebView 鍙屽悜娲惧彂杩涘害浜嬩欢銆?
---

### 5.2 鏍稿績鎶€鏈疄鐜?鍦?`src/components/debug/AlpineDevApkExtensionView.vue` 涓ˉ榻愪簡瀹屾暣鐨勫叏娴佺▼鐘舵€佹満涓庤瑙夌粍浠讹細

1. **鍘熺敓鏂偣缁紶妗ユ帴鍚姩**锛?   - 璇嗗埆鍘熺敓鐜锛坄isNativeApp.value && window.AlpineNative`锛夛紱
   - 鑷姩鐢熸垚鍞竴寮€鍙戠増鏈爣璇?`dev-${variant}-${buildCode}`锛岃皟鐢?`window.AlpineNative.downloadAndInstallApkWithSha256(downloadUrl, targetVersion, null)` 璋冭捣鍘熺敓甯搁┗涓嬭浇浠诲姟锛?   - 缃戦〉绔繚鎸佹爣鍑嗘祻瑙堝櫒 `<a>` 涓嬭浇鍏滃簳銆?2. **鍘熺敓鍙屽悜杩涘害鎬荤嚎鐩戝惉**锛?   - 鐩戝惉 `window.onAlpineDownloadProgress` 涓?`alpine-download-progress` 鑷畾涔変簨浠讹紱
   - 瀹炴椂瑙ｆ瀽 `status`锛坄downloading` / `installing` / `permission_required` / `error` / `completed`锛夈€乣percent`銆乣receivedBytes`銆乣totalBytes` 涓?`message`銆?3. **楂樺北榛戞洔鐭虫嫇鎵戦涓嬭浇杩涘害鍗＄墖**锛?   - **鍔ㄦ€佽剦鍐叉爣棰?*锛氱豢鑹插懠鍚哥伅 + 瀹炴椂妯″紡锛坄Debug` / `Release`锛夛紱
   - **寰厜娴佸姩杩涘害鏉?*锛歚.progress-fill.pulse-animated` 绾挎€ф笎鍙?+ `@keyframes progress-shimmer` 娴佸厜鍔ㄦ晥锛?   - **绮剧‘瀛楄妭缁熻**锛歚formatBytes(receivedBytes)` / `formatBytes(totalBytes)`锛堜緥濡?`19.14 MB / 29.45 MB`锛夛紱
   - **鐘舵€佹搷浣滃垎娴?*锛?     - `permission_required`锛氭樉寮忓睍绀?`馃憠 鍓嶅線璁剧疆寮€鍚湭鐭ュ簲鐢ㄥ畨瑁呮潈闄恅锛堣皟鐢?`AlpineNative.openInstallPermissionSettings()`锛夛紱
     - `installing`锛氭樉寮忓睍绀?`馃摬 閲嶆柊璋冭捣绯荤粺瀹夎鍣╜锛堣皟鐢?`AlpineNative.installDownloadedApk()`锛夛紱
     - `error`锛氭樉寮忓睍绀?`馃攧 鎭㈠/閲嶈瘯涓嬭浇`锛堝熀浜庡凡淇濈暀鐨勬湰鍦颁复鏃舵枃浠堕暱搴︼紝鐩存帴鍙戣捣 HTTP 206 缁紶锛夛紱
     - 搴曢儴杈呭姪鎺у埗锛氭敮鎸?`鉁?鍙栨秷涓嬭浇`锛堣皟鐢?`AlpineNative.cancelDownload()`锛夊強 `馃寪 鍒囨崲涓哄閮ㄦ祻瑙堝櫒涓嬭浇 鈫梎 鑷敱闄嶇骇銆?
---

### 5.3 鑷姩鍖栫鍒扮娴嬭瘯涓庣湡瀹炴覆鏌撻獙璇?缂栧啓鑷祴鑴氭湰 `scratch/verify_in_app_download_flow.py`锛屾ā鎷熺湡鏈虹幆澧冭繍琛屽苟鎴幏鍏ㄦ祦绋嬮摼璺細
- **娴嬭瘯 1锛堥厤瀵逛笌閴存潈锛?*锛氳緭鍏ュ瘑閽ヨВ閿侊紝鎴愬姛璇诲彇寮€鍙戞満鏈€鏂版瀯寤哄寘 `weekly-mountain-latest-debug.apk`锛屾寜閽睍绀?`[猬囷笍 涓嬭浇鏈湴 Debug APK  搴旂敤鍐呯画浼燷` 涓撳睘瑙掓爣锛?- **娴嬭瘯 2锛堣皟璧峰師鐢熶笅杞斤級**锛氱偣鍑讳笅杞芥寜閽紝鍑嗙‘瑙﹀彂 `AlpineNative.downloadAndInstallApkWithSha256` 骞堕攣瀹氱洰鏍囩洿杩?URL锛?- **娴嬭瘯 3锛堣繘搴﹀疄鏃舵覆鏌擄級**锛氭ā鎷?65% 浼犺緭锛岃繘搴︽潯绮惧噯娓叉煋涓?65% 瀹藉害锛屽瓧鑺傚睍绀?`19.14 MB / 29.45 MB`锛屽姩鏁堥『鐣咃紱
- **娴嬭瘯 4锛堢郴缁熸潈闄愭嫤鎴級**锛氭ā鎷熻Е鍙戞湭鐭ュ簲鐢ㄥ畨瑁呮潈闄愭嫤鎴紝鐣岄潰灞曠ず鏉冮檺寮曞鎸夐挳锛岀偣鍑昏Е鍙?`openInstallPermissionSettings`锛?- **娴嬭瘯 5锛堝畨瑁呭櫒璋冭捣锛?*锛氭ā鎷熷畨瑁呴樁娈碉紝鐐瑰嚮閲嶆柊璋冭捣绯荤粺瀹夎鍣紝鍑嗙‘瑙﹀彂 `installDownloadedApk`锛?- **娴嬭瘯 6锛堝紓甯告柇鐐逛繚鎸佷笌鎭㈠锛?*锛氭ā鎷熺綉缁滃紓甯镐腑鏂紝鐣岄潰鏄庣‘鎻愮ず淇濈暀鏂偣浣嶇疆骞舵彁渚涢噸璇曟仮澶嶆寜閽紱
- **娴嬭瘯 7锛堝彇娑堜笌澶嶄綅锛?*锛氱偣鍑诲彇娑堜笅杞斤紝鍑嗙‘瑙﹀彂 `cancelDownload` 骞跺畬鍏ㄥ钩绋冲浣嶈嚦鍒濆灏辩华鐘舵€併€?
鐢熸垚鐨勫叏娴佺▼楠岃瘉鎴浘淇濆瓨鍦?`scratch/feedback/` 鍙?Artifact 鐩綍锛?- `dev_apk_01_locked.png`锛氭湭閰嶅瀹夊叏闃叉姢閿?- `dev_apk_02_idle_paired.png`锛氶厤瀵规垚鍔熷睍绀哄簲鐢ㄥ唴缁紶鏍囪瘑
- `dev_apk_03_downloading_progress.png`锛氬簲鐢ㄥ唴鏂偣缁紶瀹炴椂杩涘害涓庡瓧鑺傛寚绀?- `dev_apk_04_permission_required.png`锛氭湭鐭ュ簲鐢ㄥ畨瑁呮潈闄愬紩瀵肩姸鎬?- `dev_apk_05_installing.png`锛氳皟璧风郴缁熷畨瑁呭櫒鐘舵€?- `dev_apk_06_error_retry.png`锛氱綉缁滀腑鏂柇鐐逛繚鐣欑姸鎬?- `dev_apk_07_reset_idle.png`锛氬彇娑堝悗骞崇ǔ澶嶄綅鐘舵€?
---

## 6. 鏈€缁堥獙璇佹寚鏍囨眹鎬?1. **Agent Feedback Monorepo 娴嬭瘯濂椾欢**锛?   - 鍏ㄥ伐浣滅┖闂?103/103 娴嬭瘯鍏ㄩ儴閫氳繃锛坄core`: 13, `client`: 29, `sentinel`: 19, `vite-plugin`: 29, `vite-demo`: 13锛夈€?2. **Weekly Mountain 鑷姩鍖栨祴璇曞浠?*锛?   - `test_resource_pack_service.js`: 9/9 閫氳繃銆?   - `test_store_multi_region.js`: 6/6 閫氳繃銆?   - `test_region_datasets.py` & `test_region_pack_builder.py`: 10/10 閫氳繃銆?   - `verify_modal_smooth.py`: 闂儊淇绔埌绔覆鏌撻€氳繃銆?   - `verify_in_app_download_flow.py`: 鏈湴鍖呭簲鐢ㄥ唴鏂偣缁紶绔埌绔€氳繃銆?3. **鏋勫缓楠岃瘉**锛?   - `npm run build`锛? 閿欒锛岃€楁椂 5.48s銆?   - `npm run build:release`锛? 閿欒锛岃€楁椂 6.20s銆?   - Gradle `assembleDebug`锛? 閿欒锛岃€楁椂 1m 50s銆?4. **瀹夊叏涓庣孩绾挎鏌?*锛?   - 鍙楅檺璇嶆眹绾㈢嚎妫€鏌ワ細0 澶勮繚瑙勩€?   - 瀵嗛挜涓庡嚟鎹槻鎶わ細鎵€鏈夊睍绀虹粺涓€鍗犱綅鑴辨晱銆?
---

## 7. 鐗堟湰杩唬涓庢湰鍦拌皟璇曞寘浜х墿褰掓。

### 7.1 agent-feedback 鍗囩骇鑷?v1.4.1
- **鐗堟湰閫掑涓庢墦鍖?*锛?  - 鏇存柊 `agent-feedback` 鏍圭洰褰曞強瀛愬寘鐗堟湰鑷?`1.4.1`锛?  - 缂栧啓 `CHANGELOG.md` 璁板綍 `[1.4.1] - 2026-11-13` 绉诲姩绔?WebView 妯℃€佸脊绐楅浂闂儊涓庣‖浠跺姞閫熶紭鍖栵紱
  - 杩愯 `pnpm pack` 鐢熸垚 4 涓?npm tarball 浜х墿骞舵墦鍖呭綊妗ｈ嚦 `releases/v1.4.1/agent-feedback-v1.4.1-npm-packages.zip`銆?- **姣忓懆涓€灞卞伐绋嬮泦鎴?*锛?  - 鏇存柊 `package.json` 渚濊禆椤圭増鏈负 `^1.4.1`锛?  - 鍚屾鐗╃悊浜х墿鑷?`node_modules/@lylyuanliang/`銆?
### 7.2 鏈湴璋冭瘯鍖呴噸鏂版瀯寤轰笌 releases 褰掓。
- **鐗堟湰鍙锋椂闂存埑鍚屾**锛?  - 杩愯 `python scripts/sync_version.py 0.3.2`锛岀増鏈崌鑷?`0.3.2.202611131340` (BuildCode: `1794548401`)銆?- **娓呯悊涓庡叏鏂扮紪璇戝綊妗?*锛?  - 娓呯悊 `releases/` 鐩綍鍘嗗彶鍐椾綑浜х墿锛?  - 杩愯 `scripts/build_app.ps1 -Variant debug -RegionVariant standard` 瀹屾垚鍏ㄦ柊鍘熺敓鏋勫缓锛?  - 鐢熸垚绾噣浜х墿锛?    - `releases/weekly-mountain-v0.3.2.202611131340-debug-standard.apk` (29.44 MB)
    - `releases/weekly-mountain-latest-debug.apk` (29.44 MB)
    - `releases/weekly-mountain-standard.apk` (29.44 MB)
  - `GET /api/app-update` 瀹炴椂鏇存柊骞舵彁渚涘氨缁笅杞姐€?
