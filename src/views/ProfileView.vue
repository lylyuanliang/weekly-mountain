<template>

  <div class="profile-view w-full min-h-screen bg-background text-on-surface pb-28 pt-[calc(14px+max(env(safe-area-inset-top,0px),16px))] px-space-lg max-w-md mx-auto space-y-space-xl select-none font-body-md">

    <!-- ================= TOP APP BAR ================= -->

    <header class="flex justify-between items-center w-full py-1">

      <div class="flex items-center gap-space-sm">

        <router-link

          to="/explore"

          aria-label="返回探索"

          class="w-8 h-8 rounded-full flex items-center justify-center text-on-surface-variant hover:text-primary active:scale-95 transition-all"

        >

          <span class="material-symbols-outlined text-[20px]">arrow_back</span>

        </router-link>

        <div class="flex flex-col">

          <span class="font-headline-md text-[16px] leading-[22px] font-bold tracking-tight text-on-surface">我的成就与设置</span>

          <span class="font-label-data-sm text-[10px] text-primary tracking-wider uppercase">Alpine Telemetry & Profile</span>

        </div>

      </div>

      <div class="flex items-center gap-1">

        <!-- 快捷主题切换胶囊 -->

        <button

          @click="themeStore.cycleTheme()"

          class="btn-cycle-theme px-2.5 py-1 rounded-full bg-surface-container-high/80 border border-white/10 text-on-surface hover:text-primary font-label-data-sm text-[11px] flex items-center gap-1 active:scale-95 transition-all"

          title="切换视觉主题"

        >

          <span class="material-symbols-outlined text-[14px] text-secondary">palette</span>

          <span>{{ currentThemeLabel }}</span>

        </button>

      </div>

    </header>



    <!-- ================= SECTION 1: Telemetry 遥测仪表盘 (Bento Glass Card) ================= -->

    <section class="telemetry-dashboard relative rounded-3xl bg-surface-container/70 border border-white/10 p-space-lg backdrop-blur-xl overflow-hidden glow-primary space-y-4">

      <!-- Ambient Glows -->

      <div class="absolute -top-12 -right-12 w-44 h-44 bg-primary/15 rounded-full blur-3xl pointer-events-none"></div>

      <div class="absolute -bottom-10 -left-10 w-36 h-36 bg-secondary/15 rounded-full blur-2xl pointer-events-none"></div>



      <!-- Top Header & Dynamic Rank Level -->

      <div class="relative z-10 flex items-start justify-between">

        <div>

          <div class="flex items-center gap-2 mb-1.5 flex-wrap">

            <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-primary/10 border border-primary/20 text-primary font-label-data-sm text-[10px]">

              <span class="material-symbols-outlined text-[13px] fill" style="font-variation-settings: 'FILL' 1;">military_tech</span>

              <span class="rank-badge">{{ checkinStore.stats.rank.level }} · {{ checkinStore.stats.rank.title }}</span>

            </div>

            <!-- 一键生成成就长图海报胶囊按钮 -->

            <button

              @click="isPosterModalOpen = true"

              class="btn-generate-poster inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-primary/15 hover:bg-primary/25 border border-primary/30 text-primary font-label-data-sm text-[10px] font-semibold active:scale-95 transition-all shadow-[0_0_10px_rgba(78,222,163,0.25)]"

              title="生成高质感成就长图海报"

            >

              <span class="material-symbols-outlined text-[12px]">photo_camera</span>

              <span>生成成就海报</span>

            </button>

          </div>

          <h2 class="font-headline-lg text-[22px] leading-tight font-bold text-on-surface tracking-tight">

            {{ regionStore.currentRegion.shortName }}峰线总完成

            <span class="text-primary font-label-data-lg text-[28px] font-bold">{{ checkinStore.stats.doneCount }}</span>

            <span class="text-on-surface-variant text-[15px]">/{{ currentRegionMountainsCount }} 座</span>

          </h2>

        </div>



        <!-- Circular Progress Widget -->

        <div class="circular-progress-widget progress-circle relative w-16 h-16 flex items-center justify-center shrink-0">

          <svg class="w-16 h-16 transform -rotate-90" viewBox="0 0 64 64">

            <circle cx="32" cy="32" fill="none" r="26" stroke="rgba(255,255,255,0.08)" stroke-width="4.5"></circle>

            <circle

              class="drop-shadow-[0_0_8px_rgba(78,222,163,0.6)] transition-all duration-700 ease-out"

              cx="32"

              cy="32"

              fill="none"

              r="26"

              stroke="#4edea3"

              stroke-dasharray="163"

              :stroke-dashoffset="163 - (163 * checkinStore.stats.completionRate) / 100"

              stroke-linecap="round"

              stroke-width="4.5"

            ></circle>

          </svg>

          <div class="absolute flex flex-col items-center">

            <span class="font-label-data-sm text-[12px] font-bold text-primary">{{ checkinStore.stats.completionRate }}%</span>

          </div>

        </div>

      </div>



      <!-- 3-Column Core Telemetry Metrics -->

      <div class="relative z-10 grid grid-cols-3 gap-2 p-2.5 rounded-xl bg-surface-container-lowest/60 border border-white/5 backdrop-blur-md">

        <div class="flex flex-col">

          <span class="font-label-data-sm text-[10px] text-on-surface-variant flex items-center gap-0.5">

            <span class="material-symbols-outlined text-[12px] text-primary">altitude</span> 累计爬升

          </span>

          <span class="font-label-data-lg text-[16px] font-bold text-on-surface mt-0.5 truncate">

            +{{ checkinStore.stats.totalAscent.toLocaleString() }}<span class="text-[10px] text-on-surface-variant ml-0.5 font-normal">m</span>

          </span>

        </div>



        <div class="flex flex-col border-x border-white/5 px-2">

          <span class="font-label-data-sm text-[10px] text-on-surface-variant flex items-center gap-0.5">

            <span class="material-symbols-outlined text-[12px] text-secondary">distance</span> 徒步总里程

          </span>

          <span class="font-label-data-lg text-[16px] font-bold text-on-surface mt-0.5 truncate">

            {{ checkinStore.stats.totalDistance }}<span class="text-[10px] text-on-surface-variant ml-0.5 font-normal">km</span>

          </span>

        </div>



        <div class="flex flex-col pl-1">

          <span class="font-label-data-sm text-[10px] text-on-surface-variant flex items-center gap-0.5">

            <span class="material-symbols-outlined text-[12px] text-tertiary">workspace_premium</span> 解锁勋章

          </span>

          <span class="font-label-data-lg text-[16px] font-bold text-on-surface mt-0.5 truncate">

            {{ unlockedBadgesCount }}<span class="text-[10px] text-on-surface-variant ml-0.5 font-normal">/4 枚</span>

          </span>

        </div>

      </div>

    </section>



    <!-- ================= SECTION 2: Bento 成就勋章网格 ================= -->

    <section class="space-y-space-md">

      <div class="flex items-center justify-between">

        <div class="flex items-center gap-2">

          <span class="w-1.5 h-4 rounded-full bg-secondary"></span>

          <h3 class="font-headline-md text-[18px] font-bold text-on-surface">Bento 成就勋章</h3>

        </div>

        <span class="font-label-data-sm text-[11px] text-secondary">

          已点亮 {{ unlockedBadgesCount }} / 4

        </span>

      </div>



      <div class="bento-badges-grid badge-grid grid grid-cols-2 gap-3">

        <!-- Badge 1: 初探者 -->

        <div

          class="bento-badge-card p-3.5 rounded-2xl border backdrop-blur-xl flex flex-col justify-between space-y-2.5 transition-all"

          :class="isFirstSummitUnlocked

            ? 'bg-surface-container/70 border-primary/30 glow-primary'

            : 'bg-surface-container/40 border-white/5 opacity-70'"

        >

          <div class="flex items-center justify-between">

            <div

              class="w-8 h-8 rounded-xl flex items-center justify-center"

              :class="isFirstSummitUnlocked ? 'bg-primary/20 text-primary' : 'bg-surface-container text-outline'"

            >

              <span class="material-symbols-outlined text-[18px]">hiking</span>

            </div>

            <span

              class="font-label-data-sm text-[9px] px-1.5 py-0.5 rounded-full border"

              :class="isFirstSummitUnlocked

                ? 'bg-primary/10 border-primary/20 text-primary'

                : 'bg-white/5 border-white/10 text-on-surface-variant'"

            >

              {{ isFirstSummitUnlocked ? '已点亮' : '待解锁' }}

            </span>

          </div>

          <div>

            <h4 class="font-headline-md text-[13px] font-bold text-on-surface">初探者</h4>

            <p class="font-body-sm text-[10px] text-on-surface-variant mt-0.5">首次登顶任意 1 座山峰</p>

          </div>

        </div>



        <!-- Badge 2: 高海拔 -->

        <div

          class="bento-badge-card p-3.5 rounded-2xl border backdrop-blur-xl flex flex-col justify-between space-y-2.5 transition-all"

          :class="isHighAltitudeUnlocked

            ? 'bg-surface-container/70 border-secondary/30 glow-secondary'

            : 'bg-surface-container/40 border-white/5 opacity-70'"

        >

          <div class="flex items-center justify-between">

            <div

              class="w-8 h-8 rounded-xl flex items-center justify-center"

              :class="isHighAltitudeUnlocked ? 'bg-secondary/20 text-secondary' : 'bg-surface-container text-outline'"

            >

              <span class="material-symbols-outlined text-[18px]">ac_unit</span>

            </div>

            <span

              class="font-label-data-sm text-[9px] px-1.5 py-0.5 rounded-full border"

              :class="isHighAltitudeUnlocked

                ? 'bg-secondary/10 border-secondary/20 text-secondary'

                : 'bg-white/5 border-white/10 text-on-surface-variant'"

            >

              {{ isHighAltitudeUnlocked ? '已点亮' : '待解锁' }}

            </span>

          </div>

          <div>

            <h4 class="font-headline-md text-[13px] font-bold text-on-surface">高海拔</h4>

            <p class="font-body-sm text-[10px] text-on-surface-variant mt-0.5">成功征服 4000m+ 极高山</p>

          </div>

        </div>



        <!-- Badge 3: 云海猎人 -->

        <div

          class="bento-badge-card p-3.5 rounded-2xl border backdrop-blur-xl flex flex-col justify-between space-y-2.5 transition-all"

          :class="isCloudHunterUnlocked

            ? 'bg-surface-container/70 border-tertiary/30 glow-tertiary'

            : 'bg-surface-container/40 border-white/5 opacity-70'"

        >

          <div class="flex items-center justify-between">

            <div

              class="w-8 h-8 rounded-xl flex items-center justify-center"

              :class="isCloudHunterUnlocked ? 'bg-tertiary/20 text-tertiary' : 'bg-surface-container text-outline'"

            >

              <span class="material-symbols-outlined text-[18px]">cloud</span>

            </div>

            <span

              class="font-label-data-sm text-[9px] px-1.5 py-0.5 rounded-full border"

              :class="isCloudHunterUnlocked

                ? 'bg-tertiary/10 border-tertiary/20 text-tertiary'

                : 'bg-white/5 border-white/10 text-on-surface-variant'"

            >

              {{ isCloudHunterUnlocked ? '已点亮' : '待解锁' }}

            </span>

          </div>

          <div>

            <h4 class="font-headline-md text-[13px] font-bold text-on-surface">云海猎人</h4>

            <p class="font-body-sm text-[10px] text-on-surface-variant mt-0.5">打卡云海日出观景名山</p>

          </div>

        </div>



        <!-- Badge 4: 环线征服者 -->

        <div

          class="bento-badge-card p-3.5 rounded-2xl border backdrop-blur-xl flex flex-col justify-between space-y-2.5 transition-all"

          :class="isLoopConquerorUnlocked

            ? 'bg-surface-container/70 border-primary/30 glow-primary'

            : 'bg-surface-container/40 border-white/5 opacity-70'"

        >

          <div class="flex items-center justify-between">

            <div

              class="w-8 h-8 rounded-xl flex items-center justify-center"

              :class="isLoopConquerorUnlocked ? 'bg-primary/20 text-primary' : 'bg-surface-container text-outline'"

            >

              <span class="material-symbols-outlined text-[18px]">explore</span>

            </div>

            <span

              class="font-label-data-sm text-[9px] px-1.5 py-0.5 rounded-full border"

              :class="isLoopConquerorUnlocked

                ? 'bg-primary/10 border-primary/20 text-primary'

                : 'bg-white/5 border-white/10 text-on-surface-variant'"

            >

              {{ isLoopConquerorUnlocked ? '已点亮' : '待解锁' }}

            </span>

          </div>

          <div>

            <h4 class="font-headline-md text-[13px] font-bold text-on-surface">环线征服者</h4>

            <p class="font-body-sm text-[10px] text-on-surface-variant mt-0.5">累计完成 5 座以上峰线</p>

          </div>

        </div>

      </div>

    </section>



    <!-- ================= SECTION 2.5: 打卡记录与实景相册 ================= -->

    <section class="space-y-space-md">

      <div class="flex items-center justify-between">

        <div class="flex items-center gap-2">

          <span class="w-1.5 h-4 rounded-full bg-primary"></span>

          <h3 class="font-headline-md text-[18px] font-bold text-on-surface">打卡实景与探索心得</h3>

        </div>

        <div class="flex items-center gap-2">

          <span class="font-label-data-sm text-[11px] text-primary">

            已打卡 {{ checkedMountainsList.length }} 座

          </span>

          <button

            @click="isPosterModalOpen = true"

            class="px-2.5 py-1 rounded-full bg-primary/15 hover:bg-primary/25 border border-primary/30 text-primary text-[11px] font-label-data-sm flex items-center gap-1 active:scale-95 transition-all shadow-sm"

          >

            <span class="material-symbols-outlined text-[13px]">palette</span>

            <span>生成海报</span>

          </button>

        </div>

      </div>



      <!-- 空打卡状态提示卡片 -->

      <div

        v-if="checkedMountainsList.length === 0"

        class="p-5 rounded-2xl bg-surface-container/50 border border-white/5 backdrop-blur-xl text-center space-y-2.5"

      >

        <span class="material-symbols-outlined text-[34px] text-outline">add_a_photo</span>

        <p class="font-body-sm text-[12px] text-on-surface-variant max-w-xs mx-auto">

          暂无打卡峰线。在山单详情中完成登顶打卡，即可在此上传高质感实景照片并生成专属成就海报！

        </p>

        <div>

          <router-link

            to="/explore"

            class="inline-flex items-center gap-1 px-3.5 py-1.5 rounded-full bg-primary/15 text-primary hover:bg-primary/25 border border-primary/30 font-label-data-sm text-[11px] font-semibold transition-all"

          >

            <span>浏览探索山单</span>

            <span class="material-symbols-outlined text-[14px]">arrow_forward</span>

          </router-link>

        </div>

      </div>



      <!-- 打卡名山卡片列表 -->

      <div v-else class="space-y-3">

        <div

          v-for="item in checkedMountainsList"

          :key="item.id"

          class="checkin-record-card p-3.5 rounded-2xl bg-surface-container/70 border border-white/10 backdrop-blur-xl space-y-3 transition-all"

        >

          <!-- 头部信息 -->

          <div class="flex items-center justify-between">

            <div class="flex items-center gap-2">

              <span class="w-2 h-2 rounded-full bg-primary"></span>

              <h4 class="font-headline-md text-[14px] font-bold text-on-surface">{{ item.name }}</h4>

              <span class="font-label-data-sm text-[10px] px-1.5 py-0.5 rounded-md bg-surface-container-high text-secondary border border-white/5">

                {{ item.altitude_m || item.alt }}m

              </span>

            </div>

            <span class="font-label-data-sm text-[10px] text-on-surface-variant">

              {{ formatCheckinDate(item.record?.checkedAt) }}

            </span>

          </div>



          <!-- 照片展示 / 上传区域 (支持 1~9 张实景相册) -->

          <div class="relative space-y-2">

            <!-- 已经有照片时的多图相册 -->

            <div v-if="getItemPhotos(item).length > 0" class="space-y-2">

              <!-- 头部工具行 -->

              <div class="flex items-center justify-between text-[11px] font-label-data-sm text-on-surface-variant">

                <span class="flex items-center gap-1.5 text-on-surface font-medium">

                  <span class="material-symbols-outlined text-[14px] text-primary">photo_library</span>

                  实景画廊 ({{ getItemPhotos(item).length }}/9)

                </span>

                <div class="flex items-center gap-2">

                  <button

                    v-if="getItemPhotos(item).length < 9"

                    @click="triggerUploadForMountain(item.id)"

                    class="text-primary hover:text-primary/80 font-medium flex items-center gap-0.5 active:scale-95 transition-transform"

                  >

                    <span class="material-symbols-outlined text-[13px]">add_photo_alternate</span>

                    <span>添加照片</span>

                  </button>

                  <button

                    @click="removeAllPhotos(item.id)"

                    class="text-on-surface-variant hover:text-error text-[10px] active:scale-95 transition-colors"

                  >

                    清空全部

                  </button>

                </div>

              </div>



              <!-- 单张照片：宽幅封面卡片展示 -->

              <div

                v-if="getItemPhotos(item).length === 1"

                class="relative rounded-xl overflow-hidden border border-white/10 bg-black/40 group cursor-pointer"

                @click="openPhotoPreview(item.id, 0)"

              >

                <img

                  :src="getItemPhotos(item)[0]"

                  :alt="item.name"

                  class="w-full h-44 object-cover"

                />

                <div class="absolute top-2 left-2 px-1.5 py-0.5 rounded-md bg-black/70 backdrop-blur-md border border-white/10 text-[9px] font-label-data-sm text-primary flex items-center gap-1">

                  <span class="w-1.5 h-1.5 rounded-full bg-primary"></span>

                  <span>主封面 (点击放大)</span>

                </div>

                <div class="absolute inset-0 bg-black/50 opacity-90 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">

                  <button

                    @click.stop="triggerUploadForMountain(item.id)"

                    class="px-2.5 py-1 rounded-lg bg-surface-container-high/90 text-primary text-[11px] font-medium flex items-center gap-1 active:scale-95 transition-transform"

                  >

                    <span class="material-symbols-outlined text-[14px]">add_photo_alternate</span>

                    添加更多

                  </button>

                  <button

                    @click.stop="openPhotoPreview(item.id, 0)"

                    class="px-2.5 py-1 rounded-lg bg-surface-container-high/90 text-on-surface text-[11px] font-medium flex items-center gap-1 active:scale-95 transition-transform"

                  >

                    <span class="material-symbols-outlined text-[14px]">fullscreen</span>

                    大图预览

                  </button>

                  <button

                    @click.stop="removePhotoAt(item.id, 0)"

                    class="px-2.5 py-1 rounded-lg bg-surface-container-high/90 text-error text-[11px] font-medium flex items-center gap-1 active:scale-95 transition-transform"

                  >

                    <span class="material-symbols-outlined text-[14px]">delete</span>

                    删除

                  </button>

                </div>

              </div>



              <!-- 多张照片 (2~9张)：三列网格画廊 -->

              <div v-else class="grid grid-cols-3 gap-2">

                <div

                  v-for="(photo, pIdx) in getItemPhotos(item)"

                  :key="pIdx"

                  class="aspect-square relative rounded-xl overflow-hidden border border-white/10 bg-black/40 group cursor-pointer"

                  @click="openPhotoPreview(item.id, pIdx)"

                >

                  <img

                    :src="photo"

                    :alt="`${item.name} 实景 ${pIdx + 1}`"

                    class="w-full h-full object-cover transition-transform duration-200 group-hover:scale-105"

                  />

                  <!-- 封面角标 -->

                  <span

                    v-if="pIdx === 0"

                    class="absolute top-1 left-1 px-1 py-0.2 rounded bg-primary/90 text-surface text-[8px] font-bold font-label-data-sm shadow-sm"

                  >

                    封面

                  </span>

                  <!-- 删除按钮 -->

                  <button

                    @click.stop="removePhotoAt(item.id, pIdx)"

                    class="absolute top-1 right-1 w-5 h-5 rounded-full bg-black/75 hover:bg-error text-white/90 flex items-center justify-center active:scale-90 transition-all opacity-90 sm:opacity-0 sm:group-hover:opacity-100"

                    title="删除此张照片"

                  >

                    <span class="material-symbols-outlined text-[12px]">close</span>

                  </button>

                </div>



                <!-- 添加更多占位格 (未满 9 张) -->

                <div

                  v-if="getItemPhotos(item).length < 9"

                  @click="triggerUploadForMountain(item.id)"

                  class="aspect-square rounded-xl border border-dashed border-white/25 hover:border-primary/50 bg-surface-container-lowest/60 flex flex-col items-center justify-center gap-1 cursor-pointer hover:bg-surface-container-lowest transition-all text-on-surface-variant hover:text-primary active:scale-95"

                >

                  <span class="material-symbols-outlined text-[20px]">add_photo_alternate</span>

                  <span class="font-label-data-sm text-[9px]">+{{ 9 - getItemPhotos(item).length }}张</span>

                </div>

              </div>

            </div>



            <!-- 尚无照片：上传引导 -->

            <div

              v-else

              @click="triggerUploadForMountain(item.id)"

              class="w-full py-4 px-3 rounded-xl border border-dashed border-white/20 hover:border-primary/40 bg-surface-container-lowest/50 flex flex-col items-center justify-center gap-1.5 cursor-pointer hover:bg-surface-container-lowest/80 transition-all text-on-surface-variant hover:text-primary"

            >

              <span class="material-symbols-outlined text-[24px]">add_a_photo</span>

              <span class="font-label-data-sm text-[11px] font-semibold">上传登顶打卡实景照片 (支持多选批量上传，最多9张)</span>

              <span class="font-label-data-sm text-[9px] text-outline">自动轻量压缩，防爆本地存储空间</span>

            </div>

          </div>



          <!-- 心得记录随笔输入 -->

          <div class="space-y-1.5">

            <div class="flex items-center justify-between font-label-data-sm text-[10px] text-on-surface-variant">

              <span class="flex items-center gap-1">

                <span class="material-symbols-outlined text-[12px] text-secondary">edit_note</span>

                探索心得与路况随笔

              </span>

              <button

                @click="saveNote(item.id)"

                class="text-primary hover:text-primary/80 font-semibold flex items-center gap-0.5 active:scale-95 transition-transform"

              >

                <span class="material-symbols-outlined text-[12px]">save</span>

                保存随笔

              </button>

            </div>

            <textarea

              v-model="notesDraft[item.id]"

              rows="2"

              placeholder="记录你的登顶心情、路况、天气或避坑建议..."

              class="w-full p-2.5 rounded-xl bg-surface-container-lowest/80 border border-white/10 text-on-surface text-[12px] font-body-sm focus:outline-none focus:border-primary/40 placeholder:text-outline-variant resize-none"

            ></textarea>

          </div>

        </div>

      </div>

    </section>



    <!-- ================= SECTION 3: 难度梯队与地貌景观分布 ================= -->

    <section class="space-y-space-md">

      <div class="p-4 rounded-2xl bg-surface-container/70 border border-white/10 backdrop-blur-xl space-y-3">

        <div class="font-label-data-sm text-[11px] font-semibold text-on-surface flex items-center justify-between">

          <span class="flex items-center gap-1.5">

            <span class="material-symbols-outlined text-[15px] text-secondary">category</span>

            地貌景观分类打卡进度

          </span>

          <span class="text-on-surface-variant text-[10px]">50 座全量归类</span>

        </div>



        <div class="space-y-2.5">

          <!-- 景观分类行 -->

          <div v-for="cat in landscapeStats" :key="cat.name" class="space-y-1">

            <div class="flex justify-between font-label-data-sm text-[11px]">

              <span class="text-on-surface flex items-center gap-1">

                <span class="material-symbols-outlined text-[13px]" :class="cat.colorClass">{{ cat.icon }}</span>

                {{ cat.name }}

              </span>

              <span class="font-semibold" :class="cat.colorClass">

                {{ cat.done }} / {{ cat.total }}

                <span class="text-on-surface-variant font-normal">({{ cat.pct }}%)</span>

              </span>

            </div>

            <div class="h-1.5 w-full bg-surface-container-lowest rounded-full overflow-hidden">

              <div

                class="h-full rounded-full transition-all duration-500"

                :class="cat.bgClass"

                :style="{ width: `${cat.pct}%` }"

              ></div>

            </div>

          </div>

        </div>

      </div>

    </section>



    <!-- ================= SECTION 4: 数据备份与恢复 + 系统设置 ================= -->

    <section class="space-y-space-md">

      <div class="flex items-center gap-2">

        <span class="w-1.5 h-4 rounded-full bg-tertiary"></span>

        <h3 class="font-headline-md text-[18px] font-bold text-on-surface">数据持久化与主题设置</h3>

      </div>



      <!-- Action Card -->

      <div class="p-3.5 rounded-2xl bg-surface-container/70 border border-white/10 backdrop-blur-xl space-y-3">

        <!-- 备份与恢复按钮组 -->

        <div class="grid grid-cols-2 gap-2">

          <button

            @click="handleExportBackup"

            class="btn-export-backup py-2.5 px-3 rounded-xl bg-surface-container-high/80 border border-white/10 hover:border-primary/40 font-body-sm text-[12px] text-on-surface flex items-center justify-center gap-1.5 active:scale-95 transition-all"

          >

            <span class="material-symbols-outlined text-[16px] text-primary">backup</span>

            <span>导出备份 (JSON)</span>

          </button>



          <button

            @click="triggerImport"

            class="py-2.5 px-3 rounded-xl bg-surface-container-high/80 border border-white/10 hover:border-secondary/40 font-body-sm text-[12px] text-on-surface flex items-center justify-center gap-1.5 active:scale-95 transition-all"

          >

            <span class="material-symbols-outlined text-[16px] text-secondary">file_download</span>

            <span>恢复备份</span>

          </button>



          <!-- 隐藏的文件上传 input -->

          <input

            ref="fileInputRef"

            type="file"

            accept=".json"

            class="hidden"

            @change="handleFileChange"

          />

        </div>



        <!-- 主题切换行 -->

        <div class="pt-2 border-t border-white/5 flex items-center justify-between">

          <div class="flex flex-col">

            <span class="font-body-md text-[13px] font-semibold text-on-surface">视觉主题</span>

            <span class="font-label-data-sm text-[10px] text-on-surface-variant">支持极光黑曜石、水墨、旷野露营</span>

          </div>



          <button

            @click="themeStore.cycleTheme()"

            class="btn-cycle-theme py-1.5 px-3 rounded-xl bg-primary text-on-primary font-body-md text-[12px] font-bold flex items-center gap-1 active:scale-95 transition-all shadow-sm"

          >

            <span class="material-symbols-outlined text-[15px]">palette</span>

            <span>切换主题 ({{ currentThemeLabel }})</span>

          </button>

        </div>

      </div>

    </section>



    <!-- ================= SECTION 5: 版本信息与数据核验公示 ================= -->

    <footer class="pt-2 pb-6 text-center space-y-2 text-on-surface-variant">

      <div class="inline-flex items-center gap-2 flex-wrap justify-center">

        <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-surface-container-high text-label-data-sm text-[10px] text-primary">

          <span class="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_4px_#4edea3]"></span>

          <span>每周一山 · {{ VERSION_LABEL }}</span>

        </div>



        <!-- 检查更新按钮 -->

        <button

          type="button"

          @click="updateStore.checkForUpdate(false)"

          :disabled="updateStore.isChecking"

          class="btn-check-update relative inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-surface-container hover:bg-surface-container-high border border-outline-variant/30 text-[10px] text-on-surface active:scale-95 transition-all"

        >

          <span class="material-symbols-outlined text-[12px]" :class="{ 'animate-spin': updateStore.isChecking }">

            {{ updateStore.isChecking ? 'progress_activity' : 'sync' }}

          </span>

          <span>{{ updateStore.isChecking ? '检测中...' : '检查更新' }}</span>

          <!-- 红点标记 -->

          <span

            v-if="updateStore.hasUpdate"

            class="w-1.5 h-1.5 rounded-full bg-red-500 shadow-[0_0_6px_#ef4444]"

          ></span>

        </button>

      </div>

      <p class="font-label-data-sm text-[10px] text-outline">

        {{ regionStore.currentRegion.title }}遥测与 GPS 轨迹核验数据已通过多源实地复核 (2025 深度核验)

      </p>



      <!-- 法律免责与安全告知常设入口 -->

      <div class="pt-2">

        <button

          type="button"

          @click="isDisclaimerModalOpen = true"

          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-surface-container/60 hover:bg-surface-container border border-white/10 text-[11px] text-gray-300 hover:text-white transition-all active:scale-95 shadow-sm"

        >

          <span class="material-symbols-outlined text-[15px] text-amber-400">gavel</span>

          <span>《户外安全公约与法律免责声明》</span>

        </button>

      </div>

    </footer>



    <!-- Toast Feedback -->

    <div

      v-if="toastMessage"

      class="fixed top-16 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-xl frost-glass-highlight text-primary text-body-sm font-semibold shadow-2xl flex items-center gap-2 transition-all duration-300"

    >

      <span class="material-symbols-outlined text-[18px]">info</span>

      <span>{{ toastMessage }}</span>

    </div>



    <!-- 隐藏的照片上传 input (支持 multiple 多选批量上传) -->

    <input

      ref="photoInputRef"

      type="file"

      accept="image/*"

      multiple

      class="hidden"

      @change="handlePhotoFileChange"

    />



    <!-- 实景照片多图全屏大图预览弹窗 (含防挖孔安全区垫高) -->

    <Teleport to="body">

      <Transition name="fade">

        <div

          v-if="isPreviewOpen"

          class="fixed inset-0 z-50 bg-black/95 backdrop-blur-md flex flex-col justify-between pt-[calc(14px+max(env(safe-area-inset-top,0px),34px))] pb-[calc(14px+max(env(safe-area-inset-bottom,0px),16px))] px-4 select-none modal-backdrop-scroll-contain"

          @click.self="isPreviewOpen = false"

          @touchmove.self.prevent

        >

          <!-- 顶栏 -->

          <div class="flex items-center justify-between text-white pb-3">

            <div class="flex items-center gap-2">

              <span class="font-bold text-[15px]">{{ currentPreviewMountain?.name }}</span>

              <span class="text-[12px] text-gray-400 font-mono">

                ({{ activePreviewPhotoIndex + 1 }} / {{ currentPreviewPhotos.length }})

              </span>

            </div>

            <button

              @click="isPreviewOpen = false"

              class="btn-close-photo-preview w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white active:scale-95 transition-all"

            >

              <span class="material-symbols-outlined text-[18px]">close</span>

            </button>

          </div>



          <!-- 图片展示区 (带左右切换手势/按钮) -->

          <div class="relative flex-1 flex items-center justify-center min-h-0 py-2">

            <img

              :src="currentPreviewPhoto"

              :alt="currentPreviewMountain?.name"

              class="max-w-full max-h-full object-contain rounded-xl shadow-2xl transition-all"

            />



            <!-- 左右切换箭头 -->

            <button

              v-if="activePreviewPhotoIndex > 0"

              @click="activePreviewPhotoIndex--"

              class="absolute left-2 w-10 h-10 rounded-full bg-black/60 hover:bg-black/80 border border-white/15 text-white flex items-center justify-center active:scale-90 transition-all"

            >

              <span class="material-symbols-outlined text-[20px]">chevron_left</span>

            </button>

            <button

              v-if="activePreviewPhotoIndex < currentPreviewPhotos.length - 1"

              @click="activePreviewPhotoIndex++"

              class="absolute right-2 w-10 h-10 rounded-full bg-black/60 hover:bg-black/80 border border-white/15 text-white flex items-center justify-center active:scale-90 transition-all"

            >

              <span class="material-symbols-outlined text-[20px]">chevron_right</span>

            </button>

          </div>



          <!-- 底部控制栏 -->

          <div class="flex items-center justify-center gap-3 pt-3 border-t border-white/10">

            <button

              v-if="activePreviewPhotoIndex > 0"

              @click="handleSetCover(activePreviewMountainId, activePreviewPhotoIndex)"

              class="px-3 py-1.5 rounded-xl bg-primary/20 border border-primary/40 text-primary text-[12px] font-medium flex items-center gap-1 active:scale-95 transition-all"

            >

              <span class="material-symbols-outlined text-[15px]">star</span>

              <span>设为主封面</span>

            </button>

            <button

              @click="handleDeletePreviewPhoto"

              class="px-3 py-1.5 rounded-xl bg-error/20 border border-error/40 text-error text-[12px] font-medium flex items-center gap-1 active:scale-95 transition-all"

            >

              <span class="material-symbols-outlined text-[15px]">delete</span>

              <span>删除此张照片</span>

            </button>

          </div>

        </div>

      </Transition>

    </Teleport>



    <!-- 高质感 Alpine Explorer 成就长图海报弹窗 -->

    <AlpineAchievementPosterModal v-model="isPosterModalOpen" />



    <!-- 户外安全公约与法律免责声明弹窗 -->

    <LegalDisclaimerModal v-model="isDisclaimerModalOpen" :mandatory="false" />



  </div>

</template>



<script setup>

import { ref, computed, reactive, watch } from 'vue';

import { useCheckinStore, compressImageToBase64 } from '@/stores/checkinStore.js';

import { useThemeStore } from '@/stores/themeStore.js';

import { useMountainStore } from '@/stores/mountainStore.js';

import { useRegionStore } from '@/stores/regionStore.js';

import AlpineAchievementPosterModal from '@/components/achievement/AlpineAchievementPosterModal.vue';

import LegalDisclaimerModal from '@/components/common/LegalDisclaimerModal.vue';

import { useUpdateStore } from '@/stores/updateStore.js';

import { useScrollLock } from '@/composables/useScrollLock.js';

import { VERSION_LABEL, IS_DEBUG_BUILD } from '@/config/version.js';



const checkinStore = useCheckinStore();

const themeStore = useThemeStore();

const mountainStore = useMountainStore();

const regionStore = useRegionStore();

const updateStore = useUpdateStore();



const isPosterModalOpen = ref(false);

const isDisclaimerModalOpen = ref(false);

const photoInputRef = ref(null);

const activeUploadMountainId = ref('');

const notesDraft = reactive({});



// 多图预览 Lightbox 状态

const isPreviewOpen = ref(false);



// 彻底杜绝底层页面背景滚动穿透

useScrollLock(isPreviewOpen);

const activePreviewMountainId = ref('');

const activePreviewPhotoIndex = ref(0);



const currentPreviewMountain = computed(() => {

  return mountainStore.getMountainById(activePreviewMountainId.value);

});



const currentPreviewRecord = computed(() => {

  return checkinStore.getCheckinRecord(activePreviewMountainId.value);

});



const currentPreviewPhotos = computed(() => {

  const r = currentPreviewRecord.value;

  if (!r) return [];

  if (Array.isArray(r.photos) && r.photos.length) return r.photos;

  return r.photoUrl ? [r.photoUrl] : [];

});



const currentPreviewPhoto = computed(() => {

  return currentPreviewPhotos.value[activePreviewPhotoIndex.value] || '';

});



function getItemPhotos(item) {

  if (!item?.record) return [];

  if (Array.isArray(item.record.photos) && item.record.photos.length) {

    return item.record.photos;

  }

  return item.record.photoUrl ? [item.record.photoUrl] : [];

}



function openPhotoPreview(mountainId, index = 0) {

  activePreviewMountainId.value = mountainId;

  activePreviewPhotoIndex.value = index;

  isPreviewOpen.value = true;

}



function handleSetCover(mountainId, index) {

  checkinStore.setCheckinCoverPhoto(mountainId, index);

  activePreviewPhotoIndex.value = 0;

  showToast('已将该照片设为主封面！');

}



function handleDeletePreviewPhoto() {

  const mId = activePreviewMountainId.value;

  const idx = activePreviewPhotoIndex.value;

  checkinStore.removeCheckinPhotoAt(mId, idx);

  showToast('已删除该照片');

  const photos = currentPreviewPhotos.value;

  if (photos.length === 0) {

    isPreviewOpen.value = false;

  } else if (activePreviewPhotoIndex.value >= photos.length) {

    activePreviewPhotoIndex.value = photos.length - 1;

  }

}



function removePhotoAt(mountainId, photoIndex) {

  checkinStore.removeCheckinPhotoAt(mountainId, photoIndex);

  showToast('已删除该照片');

}



function removeAllPhotos(mountainId) {

  checkinStore.removeCheckinPhoto(mountainId);

  showToast('已清空该山峰全部实景照片');

}



// 初始化心得随笔草稿

watch(

  () => checkinStore.checkedIds,

  (ids) => {

    (ids || []).forEach((id) => {

      if (notesDraft[id] === undefined) {

        const rec = checkinStore.getCheckinRecord(id);

        notesDraft[id] = rec?.note || '';

      }

    });

  },

  { immediate: true }

);



const checkedMountainsList = computed(() => {

  return checkinStore.checkedIds

    .map((id) => {

      const m = mountainStore.getMountainById(id);

      if (!m) return null;

      return {

        ...m,

        record: checkinStore.getCheckinRecord(id) || {}

      };

    })

    .filter(Boolean);

});



function triggerUploadForMountain(mountainId) {

  activeUploadMountainId.value = mountainId;

  if (photoInputRef.value) {

    photoInputRef.value.click();

  }

}



async function handlePhotoFileChange(event) {

  const files = Array.from(event.target.files || []);

  const targetId = activeUploadMountainId.value;

  if (!files.length || !targetId) return;



  const record = checkinStore.getCheckinRecord(targetId);

  const existingCount = record?.photos?.length || (record?.photoUrl ? 1 : 0);

  const available = 9 - existingCount;



  if (available <= 0) {

    showToast('该山峰照片已达 9 张上限');

    event.target.value = '';

    activeUploadMountainId.value = '';

    return;

  }



  const toProcess = files.slice(0, available);

  if (files.length > available) {

    showToast(`单座山最多支持 9 张，本次将处理前 ${available} 张`);

  } else {

    showToast(`正在压缩优化 ${toProcess.length} 张照片...`);

  }



  try {

    const compressedList = await Promise.all(

      toProcess.map((f) => compressImageToBase64(f, 960, 0.72))

    );

    checkinStore.addCheckinPhotos(targetId, compressedList);

    showToast(`成功添加 ${compressedList.length} 张打卡实景！`);

  } catch (err) {

    console.error('Photo upload failed:', err);

    showToast('照片处理失败，请重试');

  } finally {

    event.target.value = '';

    activeUploadMountainId.value = '';

  }

}



function removePhoto(mountainId) {

  checkinStore.removeCheckinPhoto(mountainId);

  showToast('已移除该山峰打卡照片');

}



function saveNote(mountainId) {

  const note = notesDraft[mountainId] || '';

  checkinStore.saveCheckinDetail(mountainId, { note });

  showToast('登顶心得随笔已保存！');

}



function formatCheckinDate(isoStr) {

  if (!isoStr) return '';

  try {

    const d = new Date(isoStr);

    const y = d.getFullYear();

    const m = String(d.getMonth() + 1).padStart(2, '0');

    const day = String(d.getDate()).padStart(2, '0');

    return `${y}.${m}.${day} 登顶`;

  } catch (e) {

    return '';

  }

}



const currentRegionMountainsCount = computed(() => {

  const regId = regionStore.currentRegionId;

  return mountainStore.mountains.filter((m) => !m.region_id || m.region_id === regId).length;

});



const fileInputRef = ref(null);

const toastMessage = ref('');

let toastTimer = null;



function showToast(msg) {

  toastMessage.value = msg;

  if (toastTimer) clearTimeout(toastTimer);

  toastTimer = setTimeout(() => {

    toastMessage.value = '';

  }, 2200);

}



const currentThemeLabel = computed(() => {

  switch (themeStore.theme) {

    case 'ink':

      return '水墨江南';

    case 'camp':

      return '旷野露营';

    case 'stitch':

    default:

      return '极光黑曜石';

  }

});



// Bento 勋章解锁逻辑

const isFirstSummitUnlocked = computed(() => checkinStore.stats.doneCount >= 1);



const isHighAltitudeUnlocked = computed(() => {

  return checkinStore.checkedIds.some((id) => {

    const m = mountainStore.getMountainById(id);

    return m && (m.altitude_m >= 4000);

  });

});



const isCloudHunterUnlocked = computed(() => {

  return checkinStore.checkedIds.some((id) => {

    const m = mountainStore.getMountainById(id);

    return m && (m.group === 'A' || m.highlights?.some((h) => h.includes('云海')));

  });

});



const isLoopConquerorUnlocked = computed(() => checkinStore.stats.doneCount >= 5);



const unlockedBadgesCount = computed(() => {

  let count = 0;

  if (isFirstSummitUnlocked.value) count++;

  if (isHighAltitudeUnlocked.value) count++;

  if (isCloudHunterUnlocked.value) count++;

  if (isLoopConquerorUnlocked.value) count++;

  return count;

});



// 地貌景观分类统计

const landscapeStats = computed(() => {

  const configs = [

    { key: 'A', name: '云海日出', icon: 'cloud', colorClass: 'text-secondary', bgClass: 'bg-secondary' },

    { key: 'B', name: '雪山远眺', icon: 'ac_unit', colorClass: 'text-primary', bgClass: 'bg-primary' },

    { key: 'C', name: '森林瀑布', icon: 'forest', colorClass: 'text-primary-fixed', bgClass: 'bg-primary-container' },

    { key: 'D', name: '红叶彩林', icon: 'park', colorClass: 'text-tertiary', bgClass: 'bg-tertiary' },

    { key: 'E', name: '古道人文', icon: 'temple_buddhist', colorClass: 'text-on-surface-variant', bgClass: 'bg-outline' }

  ];



  return configs.map((c) => {

    const list = mountainStore.mountains || [];

    const allInGroup = list.filter((m) => m.group === c.key);

    const total = allInGroup.length || 1;

    const done = allInGroup.filter((m) => checkinStore.isDone(m.id)).length;

    const pct = Math.round((done / total) * 100);

    return {

      ...c,

      done,

      total,

      pct

    };

  });

});



function handleExportBackup() {

  const jsonStr = checkinStore.exportBackup();

  // 复制到剪贴板

  try {

    if (navigator?.clipboard?.writeText) {

      navigator.clipboard.writeText(jsonStr);

    }

  } catch (e) {}



  // 触发 JSON 文件下载

  try {

    const blob = new Blob([jsonStr], { type: 'application/json' });

    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');

    a.href = url;

    a.download = `weekly-mountain-backup-${new Date().toISOString().slice(0, 10)}.json`;

    document.body.appendChild(a);

    a.click();

    document.body.removeChild(a);

    URL.revokeObjectURL(url);

  } catch (e) {}



  showToast('备份数据已导出下载并复制到剪贴板！');

}



function triggerImport() {

  if (fileInputRef.value) {

    fileInputRef.value.click();

  }

}



function handleFileChange(event) {

  const file = event.target.files?.[0];

  if (!file) return;



  const reader = new FileReader();

  reader.onload = (e) => {

    const content = e.target?.result;

    if (content) {

      const ok = checkinStore.importBackup(content);

      if (ok) {

        showToast('备份数据恢复成功！');

      } else {

        showToast('备份文件格式不正确，恢复失败');

      }

    }

  };

  reader.readAsText(file);

  event.target.value = '';

}

</script>



<style scoped>

.frost-glass-highlight {

  background: rgba(28, 31, 41, 0.92);

  backdrop-filter: blur(20px);

  border: 1px solid rgba(78, 222, 163, 0.3);

}

</style>
