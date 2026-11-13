# 涓婚锛氬叏鍥藉鍦板煙鎵╁睍涓?APK 鍔ㄦ€佽祫婧愬寘锛堟寜闇€涓嬭浇/鍗歌浇锛夊垎鍖呮灦鏋勮惤鍦颁笌閲嶅簡 36 宄版暟鎹叆搴?
- 褰撳墠鐘舵€侊細宸插畬鎴?(completed)
- 娑夊強闃舵锛?  1. 閲嶅簡 36 搴у悕灞辨繁搴︿簨瀹為噰闆嗐€佽埅杩瑰湴鏍囨暣鍚堜笌鍚堣瀹¤锛? 澶у湴鐞嗗垎鍖哄苟鍙戦噰闆嗭級
  2. 鍦板煙鏁版嵁鐩綍鍒嗘不鏍囧噯鍖栵紙`src/data/regions/chengdu/`, `src/data/regions/chongqing/`锛?  3. 鑷姩鍖栧湴鍩熻祫婧愬寘鏋勫缓宸ュ叿锛坄scripts/build_region_packs.py`锛岀敓鎴愬甫鏈?SHA-256 涓庣簿鍑嗗ぇ灏忕殑绂荤嚎 zip 鍖咃級
  4. 瀹㈡埛绔祫婧愬寘鍔ㄦ€佺鐞嗗櫒锛坄src/services/resourcePackService.js`锛屾敮鎸?Web 鐩磋繛涓?Native Capacitor Filesystem 鍙岃建鑷€傚簲锛?  5. Pinia 鐘舵€佺鐞嗗眰鍝嶅簲寮忕儹鎸傝浇锛坄regionStore.js` 涓?`mountainStore.js` 寮傛鑱斿姩锛屽湴鍥剧劍鐐逛笌璺濈鍩哄噯鑷€傚簲锛?  6. 鐣岄潰浜や簰涓庤祫婧愮鐞嗛潰鏉匡紙`RegionPickerSheet.vue` 鍦板煙鍒囨崲鎶藉眽涓?`ProfileView.vue` 绂荤嚎璧勬簮绠＄悊 Bento 鍗＄墖锛?  7. 鍘熺敓 APK 澶氬彉浣撴瀯寤虹煩闃碉紙`scripts/build_app.ps1 -RegionVariant standard|full`锛変笌鍏ㄩ噺 Web 鍏嶅畨瑁呬綋楠岄獙璇?- 鎭㈠鍏ュ彛锛?  - 鏁版嵁婧愰厤缃細[`src/data/regions.json`](file:///d:/file_save/workspace/github/weekly-mountain/src/data/regions.json)
  - 瀹㈡埛绔湇鍔★細[`src/services/resourcePackService.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/services/resourcePackService.js)
  - 鐘舵€佺鐞嗭細[`src/stores/regionStore.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/stores/regionStore.js), [`src/stores/mountainStore.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/stores/mountainStore.js)
  - UI 缁勪欢锛歔`src/components/common/RegionPickerSheet.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/common/RegionPickerSheet.vue), [`src/views/ProfileView.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/views/ProfileView.vue)
  - 鎵撳寘鑴氭湰锛歔`scripts/build_region_packs.py`](file:///d:/file_save/workspace/github/weekly-mountain/scripts/build_region_packs.py), [`scripts/build_app.ps1`](file:///d:/file_save/workspace/github/weekly-mountain/scripts/build_app.ps1)

---

## 涓€銆佺洰鏍囦笌鏋舵瀯鑳屾櫙

涓轰簡婊¤冻搴旂敤浠庛€婃垚閮藉懆杈?51 搴у悕灞便€嬫嫇灞曡嚦閲嶅簡涔冭嚦鍏ㄥ浗鍚嶅北鐨勬垬鐣ユ紨杩涳紝鍚屾椂閬垮厤鍥犳敹褰曞北宄般€佽埅杩广€佸浘鍐屽闀垮鑷村師鐢?APK 瀹夎鍖呮€ュ墽鑶ㄨ儉锛圓PK Bloat锛夛紝椤圭洰姝ｅ紡钀藉湴銆屾寜闇€鍦板煙璧勬簮鍖咃紙Dynamic Resource Pack锛夈€嶆灦鏋勶細

1. **闈欐€?Web 绔?(Cloudflare Pages)**锛?   - 淇濇寔鍏ㄩ噺鍦ㄧ嚎鍗崇敤浣撻獙锛堥浂瀹夎銆侀浂涓嬭浇鎽╂摝锛夛紱
   - Vite 鍔ㄦ€佸垎鍖咃紙Dynamic Chunks锛夛紝鐢ㄦ埛鍒囨崲鍦板煙鏃朵粎缃戠粶鍔犺浇鍑犲崄 KB 鐨勫紓姝ユ暟鎹?Chunk銆?2. **绉诲姩绔師鐢?APK (Android / Capacitor)**锛?   - **榛樿鏍囧噯鐗?(`-RegionVariant standard`)**锛氫粎棰勭疆鍐呯疆鎴愰兘鍛ㄨ竟 51 搴у悕灞卞簳搴э紝瀹夎鍖呬繚鎸佹瀬鑷磋交閲忥紱
   - **搴旂敤鍐呮寜闇€涓嬭浇**锛氱敤鎴峰湪銆屽湴鍩熼€夋嫨銆嶆垨銆屼釜浜轰腑蹇冦€嶅彲涓€閿粠鍔犻€熼暅鍍?Release 涓嬭浇骞惰В鍘嬮噸搴嗙瓑澶栭儴鍦板煙绂荤嚎鍖呰嚦 `Directory.Data/packs/<regionId>/`锛?   - **瀹夊叏鍗歌浇閲婃斁瀛樺偍**锛氭墿灞曞湴鍩熸敮鎸佷竴閿畨鍏ㄥ嵏杞藉苟閲婃斁鐗╃悊纾佺洏锛屾垚閮介粯璁ゅ熀绾块攣瀹氫繚鎶わ紱
   - **鍏ㄩ噺绂荤嚎鐗?(`-RegionVariant full`)**锛氭彁渚涚绾块缃墦鍖呮ā寮忥紝鏀寔涓€娆℃€ф墦鍏ユ墍鏈夋椿璺冨湴鍩燂紝閫傞厤鏃犱俊鍙锋埛澶栨瀬绔満鏅€?
---

## 浜屻€侀噸搴?36 搴у悕灞卞叏閲忔暟鎹噰闆嗕笌鏀跺綍娓呭崟

鏁版嵁缁?4 缁勫苟鍙戝瓙浠ｇ悊娣卞叆鎸栨帢鍏紑娴嬬粯涓庢埛澶栧疄娴嬭埅杩癸紝鍏辫鏀跺綍 **36 搴у悕灞便€?08 鏉＄簿缁嗚矾绾?*锛?00% 瀵归綈楂樺北鎷撴墤鏋舵瀯锛堟捣鎷斻€佽溅绋嬨€佺埇鍗囥€丩1-L5 闅惧害鍒嗙骇銆佸湴鏍囪埅杩圭偣楂樼▼搴忓垪銆侀伩鍧戜笌澶忓浼忔棻鏆存檼闃叉殤棰勮绛夛級锛?
### 1. Zone 1锛氫富鍩庘€滃洓灞扁€濅笌杩戦儕鏍稿績锛?搴э級
- **缂欎簯灞?* (1050m 路 鍖楃鍖? 路 **姝屼箰灞?* (693m 路 娌欏潽鍧濆尯) 路 **鍗楀北** (682m 路 鍗楀哺鍖? 路 **閾佸北鍧?* (584m 路 姹熷寳鍖? 路 **鐓ф瘝灞?* (461m 路 娓濆寳鍖? 路 **灏栧垁灞?* (556m 路 涔濋緳鍧″尯) 路 **閾滈敚灞?* (718m 路 娓濆寳鍖? 路 **涓灞?* (708m 路 娌欏潽鍧?涔濋緳鍧? 路 **妯靛潽灞?* (750m 路 宸村崡鍖?

### 2. Zone 2锛氭笣瑗夸笌宸濅笢杩囨浮甯﹀悕灞憋紙9搴э級
- **閲戝垁宄÷峰崕钃ュ北鑴?* (1316m 路 鍖楃鍖? 路 **鑼跺北绔规捣路钖勫垁宀?* (1025m 路 姘稿窛鍖? 路 **鍙ゅ墤灞甭烽浮鍏槾** (1300m 路 缍︽睙鍖? 路 **涓囩洓榛戝北璋仿风嫯瀛愬嘲** (1973m 路 涓囩洓缁忓紑鍖? 路 **鍦ｇ伅灞?* (1064m 路 宸村崡鍖? 路 **鐠у北浜戦浘灞甭风噧鐏宄?* (885m 路 鐠у北鍖? 路 **閾滄宸村渤灞甭烽鐐夊嘲** (778m 路 閾滄鍖? 路 **鑳滃ぉ婀柭峰亸宀╁悗灞?* (750m 路 鍖楃鍖? 路 **绠曞北路鐭崇瑡灞?* (916m 路 姹熸触/姘稿窛)

### 3. Zone 3锛氭笣涓滃崡澶у▌灞辩郴涓庢闄靛北鑴夊悕灞憋紙9搴э級
- **閲戜經灞?* (2238m 路 鍗楀窛鍖? 路 **灞辩帇鍧?* (1570m 路 鍗楀窛鍖? 路 **鏌忔灄鍙?* (1620m 路 鍗楀窛鍖? 路 **浠欏コ灞?* (2033m 路 姝﹂殕鍖? 路 **澶╃敓涓夋ˉ路鍚庡潽澶╁潙** (1200m 路 姝﹂殕鍖? 路 **姝﹂櫟灞卞ぇ瑁傝胺** (1980m 路 娑櫟鍖? 路 **鎽╁洿灞?* (1600m 路 褰按鍘? 路 **妗冭姳婧惵峰ぇ榛戝北** (1696m 路 閰夐槼鍘? 路 **鑿佸潩灞?* (2028m 路 鍗楀窛鍖?

### 4. Zone 4锛氭笣涓滃寳涓夊场宄℃睙涓庡ぇ宸村北鑴夊悕灞憋紙9搴э級
- **涓夊场涔嬪穮路璧ょ敳灞?* (1388m 路 濂夎妭鍘? 路 **鐧藉笣鍩幝疯崏鍫傚场** (245m 路 濂夎妭鍘? 路 **宸北绁炲コ宄奥锋湜闇?* (860m 路 宸北鍘? 路 **闃存潯宀峰ぇ宸村北灞嬭剨** (2796.8m 閲嶅簡鏈€楂樺嘲 路 宸邯鍘? 路 **绾㈡睜鍧澛蜂簯涓竾浜╄姳娴疯崏鍦?* (2630m 路 宸邯鍘? 路 **浜戦緹灞甭锋偓宕栭噹濂㈣崏鐢?* (1028m 路 娓濆寳/闀垮) 路 **榫欑几路宀愬北鑽夊師** (1650m 路 浜戦槼鍘? 路 **涓冩洔灞甭峰ぇ椋庡牎** (1934m 路 鐭虫煴鍘? 路 **浜㈣胺路澶у反灞卞场璋?* (2680m 路 鍩庡彛鍘?

---

## 涓夈€佸疄鏂藉畬鎴愪氦浠樻竻鍗?(Task 1 ~ Task 6)

### 1. 鏁版嵁灞傝縼绉讳笌绂荤嚎鍖呮瀯寤?(Task 1 & Task 2)
- [`src/data/regions/chengdu/mountains.json`](file:///d:/file_save/workspace/github/weekly-mountain/src/data/regions/chengdu/mountains.json)锛氭爣鍑嗗寲褰掗泦 51 搴ф垚閮藉懆杈瑰悕宄帮紱
- [`src/data/regions/chongqing/mountains.json`](file:///d:/file_save/workspace/github/weekly-mountain/src/data/regions/chongqing/mountains.json)锛氳鑼冭閰?36 搴ч噸搴嗗懆杈瑰悕宄帮紱
- [`scripts/build_region_packs.py`](file:///d:/file_save/workspace/github/weekly-mountain/scripts/build_region_packs.py)锛氭瀯寤虹嫭绔?Zip 绂荤嚎鍖咃紝鑷姩璁＄畻绮剧‘瀛楄妭鏁颁笌 SHA-256 鏁ｅ垪骞跺洖鍐欒嚦 `regions.json`锛?  - `dist-packs/pack-chengdu-v1.0.0.zip` (453,590 瀛楄妭, SHA-256 `21a8114c...`)
  - `dist-packs/pack-chongqing-v1.0.0.zip` (87,364 瀛楄妭, SHA-256 `aff164c1...`)

### 2. 瀹㈡埛绔湇鍔′笌鐘舵€佺鐞?(Task 3 & Task 4)
- [`src/services/resourcePackService.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/services/resourcePackService.js)锛氱粺涓€绠＄悊 `isPackInstalled`銆乣loadRegionMountains`銆乣downloadAndInstallPack`銆乣uninstallPack`銆乣getStorageUsage`锛涘叿澶?SHA-256 瀹屾暣鎬ч槻绡℃敼鏍￠獙涓庢枃浠剁己澶?鎹熷潖鑷姩浼橀泤闄嶇骇鍥為€€鏈哄埗锛?- [`src/stores/regionStore.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/stores/regionStore.js)锛氬搷搴斿紡绠＄悊 `installedPacks`銆乣downloadProgress` 鍙婁笅杞?鍗歌浇寮傛鍔ㄤ綔锛?- [`src/stores/mountainStore.js`](file:///d:/file_save/workspace/github/weekly-mountain/src/stores/mountainStore.js)锛氶噸鏋勪负鍝嶅簲寮忕儹鎸傝浇鏋舵瀯锛屾敮鎸佽繍琛屾椂鐑垏鎹㈠湴鍩熷苟鑷€傚簲閲嶇畻鐩爣鍦板煙涓績涓庡北宄?Haversine 鐩稿璺濈銆?
### 3. 鐢ㄦ埛鐣岄潰涓庝氦浜掗潰鏉?(Task 5)
- [`src/components/common/RegionPickerSheet.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/components/common/RegionPickerSheet.vue)锛?  - Web 绔憟鐜般€屽湪绾垮嵆鐢ㄣ€嶅井鍏夊姩鏁堬紱
  - 鍘熺敓绔憟鐜般€屽凡灏辩华銆?銆岀害 87KB 涓嬭浇绂荤嚎鍖呫€?銆屼笅杞戒腑鐧惧垎姣旇繘搴︽潯銆嶏紱
- [`src/views/ProfileView.vue`](file:///d:/file_save/workspace/github/weekly-mountain/src/views/ProfileView.vue)锛?  - Section 4 澧炶銆岀绾垮湴鍩熻祫婧愮鐞嗐€岯ento 鍗＄墖锛屽姩鎬佹牳绠楁湰鍦扮鐩樺紑閿€锛?  - 鎴愰兘鍛ㄨ竟甯︽湁銆屽熀绾夸繚鎶ゃ€嶉攣鏍囷紱閲嶅簡鍛ㄨ竟鏀寔涓嬭浇涓庡畨鍏ㄥ嵏杞藉脊绐楃‘璁ゃ€?
### 4. 鎵撳寘鑴氭湰涓?Web 鍏ㄩ噺鏍￠獙 (Task 6)
- [`scripts/build_app.ps1`](file:///d:/file_save/workspace/github/weekly-mountain/scripts/build_app.ps1)锛氬弬鏁板崌绾ф敮鎸?`-RegionVariant standard|full` 涓庡墠缃垎鍖呰嚜鍔ㄥ寲锛屽叏閲忔瀯寤哄寘瑁瑰畨鍏ㄥ洖婊氭満鍒讹紱
- Web 鐢熶骇鏋勫缓 (`npm run build:release`) 鍖呭惈鍏ㄩ噺鐙珛鍦板煙 chunks (`mountains-ZeDBaA57.js`, `mountains-ChprUGpF.js`)銆?
---

## 鍥涖€佽嚜娴嬮獙璇佺粨鏋滀笌璇佹嵁璁板綍

鍏ㄥ鑷姩鍖栨祴璇曞浠剁粡澶氭涓ユ牸鍥炲綊锛屽叏閮?100% 缁跨伅閫氳繃锛?
| 娴嬭瘯鏂囦欢 | 楠岃瘉鑼冨洿 | 缁撴灉 |
|---|---|---|
| `tests/test_region_datasets.py` | 楠岃瘉鎴愰兘 51 宄颁笌閲嶅簡 36 宄版暟鎹畬鏁存€с€両D 鍞竴鎬т笌鍙楅檺璇嶆壂鎻?| **5/5 PASS** |
| `tests/test_region_pack_builder.py` | 楠岃瘉 zip 鍖呯墿鐞嗙粨鏋勩€乵ountains.json 鏍圭骇瀛樺湪銆丼HA-256 涓庡ぇ灏忎竴鑷存€?| **5/5 PASS** |
| `tests/test_resource_pack_service.js` | 楠岃瘉 Web/Native 鍙岃建鑷€傚簲銆佷笅杞借В鍘嬨€丼HA-256 鏍￠獙銆佹崯鍧忎紭闆呴檷绾т笌鍗歌浇閲婃斁 | **9/9 PASS** |
| `tests/test_store_multi_region.js` | 楠岃瘉 Pinia 鍔ㄦ€佺儹鎸傝浇銆侀噸搴?36 宄板垏鎹€佸熀鍑嗕腑蹇冭窛绂婚噸绠椾笌寮傚父瀹归敊 | **6/6 PASS** |
| `scratch/test_ui_pack_management.py` | Playwright E2E 鍏ㄦ祦绋嬪洖褰掞紙Web 鍒囨崲銆佸師鐢熸ā鎷熴€丳rofile 鍗＄墖灞曠ず涓?DOM 鎵弿锛?| **6/6 PASS** |
| `scratch/test_build_matrix.py` | PowerShell AST 瑙ｆ瀽銆佸鍙樹綋璋冪敤婕旂粌銆佽嚜鍔ㄥ洖婊氭満鍒朵笌 Web chunks 鏍￠獙 | **5/5 PASS** |
| `npm run build:release` | 鍓嶇鐢熶骇鎵撳寘涓?Android assets 鍚屾 | **0 閿欒椤哄埄閫氳繃** |

### E2E 鐣岄潰鑷姩鍖栭獙璇佺暀妗ｆ埅鍥?- `artifacts/task5_01_region_sheet_web.png` (Web 妯″紡鍦板煙閫夋嫨鎶藉眽锛氭垚閮?51 搴т笌閲嶅簡 36 搴у潎鏍囪銆屽湪绾垮嵆鐢ㄣ€?
- `artifacts/task5_02_explore_chongqing_36peaks.png` (鍏ㄦ櫙鍦板浘涓庡崱鐗囨娊灞夌儹杞藉叆閲嶅簡 36 TRACKS锛岀紮浜戝北灞呬腑灞曠幇)
- `artifacts/task5_03_profile_pack_management_web.png` (涓汉涓績 Section 4銆岀绾垮湴鍩熻祫婧愮鐞嗐€嶅崱鐗囧憟鐜?
- `artifacts/task5_04_profile_pack_management_native.png` (妯℃嫙鍘熺敓绔幆澧冧笅鐨勫垎鍖呭ぇ灏忎笌绠＄悊鐣岄潰)

---

## 浜斻€佹硶寰嬩笌鍚堣绾㈢嚎瀹℃煡缁撹

1. **鍙楅檺鑳屼功璇嶆眹缁濆绂佷护妫€娴?*锛?   - 鍏ㄩ噺鏁版嵁鏂囦欢锛坄src/data/regions/`锛夈€佷笟鍔℃簮鐮侊紙`src/`锛夈€佹墦鍖呰剼鏈紙`scripts/`锛夈€佹瀯寤轰骇鐗╋紙`dist/`锛夊強鍘嬬缉鍖咃紙`dist-packs/`锛夊潎閫氳繃鑷姩鍖栨鍒欐壂鎻忥紱
   - 鐢熶骇浠ｇ爜涓庢暟鎹祫浜т腑杩濊鍙楅檺璇嶅懡涓鏁颁弗鏍间负 **0 澶?*锛?   - 缁熶竴閲囩敤鈥滄櫙鍖哄叕甯冨彛寰勨€濄€佲€滈棬甯傛寕鐗屼环鈥濄€佲€滄帹鑽愯矾绾库€濄€佲€滄瑙勬笭閬撯€濄€佲€滃叕寮€瀹炴祴鑸抗鈥濈瓑瀹㈣涓珛鍚堣鐢ㄨ銆?2. **Git 鎻愪氦闂ㄧ閬靛惊**锛?   - 鏁翠釜澶氫换鍔℃墽琛屽懆鏈熷唴涓ユ牸閬靛惊椤圭洰瑙勭害锛?*鏈搮鑷墽琛屼换浣?`git commit`**锛屼唬鐮佸潎澶勪簬绾噣鍙帶鐘舵€併€?3. **鏁忔劅鍑嵁鏍告煡**锛?   - 闆?API Key銆乀oken 鎴栨晱鎰熶俊鎭槑鏂囨硠闇层€?
---

## 鍏€佷氦浠樻€荤粨涓庡悗缁仮澶嶅叆鍙?
鍏ㄥ浗澶氬湴鍩熸墿灞曚笌鍔ㄦ€佽祫婧愬寘鏋舵瀯锛堥噸搴嗛鍙戠珯锛夊凡鍏ㄩ儴钀藉湴灏辩华銆?鍚庣画濡傞渶鏂板涓嬩竴鍦板煙锛堝绉﹀箔銆佹粐涓級锛屽彧闇€锛?1. 鍦?`src/data/regions/<newRegion>/mountains.json` 褰曞叆灞卞嘲鏁版嵁锛?2. 鍦?`src/data/regions.json` 娉ㄥ唽鍦板煙閰嶇疆锛?3. 杩愯 `python scripts/build_region_packs.py` 鐢熸垚瀵瑰簲鍦板煙绂荤嚎鍖呭嵆鍙紝瀹㈡埛绔笌鎵撳寘娴佹按绾垮皢鍏ㄨ嚜鍔ㄦ劅鐭ュ苟鎺ュ叆锛?
