<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="visible"
        class="fixed inset-0 z-[150] bg-black/85 backdrop-blur-md flex flex-col items-center justify-end sm:justify-center p-0 sm:p-4 select-none"
        @click.self="onBackdropClick"
      >
        <div
          class="w-full max-w-lg max-h-[92vh] bg-[#161a24] border-t sm:border border-white/10 rounded-t-3xl sm:rounded-3xl shadow-2xl flex flex-col overflow-hidden text-on-surface pt-3 pb-[calc(16px+max(env(safe-area-inset-bottom,0px),8px))] px-4 space-y-3"
        >
          <!-- 弹窗顶栏 -->
          <div class="flex items-center justify-between border-b border-white/10 pb-3 pt-1">
            <div class="flex items-center gap-2 min-w-0">
              <span class="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse"></span>
              <h3 class="text-headline-md font-bold text-white text-[15px] truncate">
                户外安全须知与法律免责声明
              </h3>
            </div>
            <button
              v-if="!mandatory"
              @click="handleClose"
              class="w-8 h-8 rounded-full bg-surface-container-high/80 border border-white/10 hover:border-primary/40 flex items-center justify-center text-on-surface-variant hover:text-white active:scale-95 transition-all"
              aria-label="关闭声明弹窗"
            >
              <span class="material-symbols-outlined text-[18px]">close</span>
            </button>
          </div>

          <!-- 可滚动免责协议正文 -->
          <div class="flex-1 overflow-y-auto space-y-3.5 pr-1 py-1 text-[12px] text-gray-300 leading-relaxed font-body-sm select-text">
            <div class="p-3 rounded-2xl bg-amber-500/10 border border-amber-400/20 text-amber-300 text-[11px] flex items-start gap-2">
              <span class="material-symbols-outlined text-[16px] text-amber-400 shrink-0 mt-0.5">warning</span>
              <span>
                <strong>敬告户外同行者：</strong>山野壮丽，敬畏同行。在开启户外探索前，请务必充分评估自身体能与天气装备，仔细阅读本法律公约与安全免责条款。
              </span>
            </div>

            <div class="space-y-1.5">
              <h4 class="font-bold text-white text-[13px] flex items-center gap-1.5">
                <span class="text-primary font-mono font-bold">1.</span>
                <span>自甘风险与自主决策（《民法典》第 1176 条）</span>
              </h4>
              <p class="text-gray-300">
                高山徒步、攀登与越野属于具有固有客观危险性的体育运动，可能面临包括但不限于高原反应、恶劣气候突变、失温、滑坠落石、野生动物侵扰、迷途及野外通信中断等不可预知的生命健康与财产安全风险。根据《中华人民共和国民法典》第一千一百七十六条（自甘风险原则），您作为完全民事行为能力人，自愿参与高山户外活动，应对个人出行决策及人身安全承担全部与最终责任。
              </p>
            </div>

            <div class="space-y-1.5">
              <h4 class="font-bold text-white text-[13px] flex items-center gap-1.5">
                <span class="text-primary font-mono font-bold">2.</span>
                <span>数据性质：理论参考，非专业向导保证</span>
              </h4>
              <p class="text-gray-300">
                本应用所收录之山峰坐标、海拔高程、徒步距离、累计爬升、路线规划及耗时估算，均为基于开源测绘及历史登山爱好者经验整理之理论参考数据，不构成任何形式的官方营运保证或专业向导承诺。实际行程耗时与难度受季节地貌、山体滑坡、风雪天气、负重与个人体能差异影响巨大，请务必预留充裕的日照与安全冗余时间，严禁盲目赶路与危险夜爬。
              </p>
            </div>

            <div class="space-y-1.5">
              <h4 class="font-bold text-white text-[13px] flex items-center gap-1.5">
                <span class="text-primary font-mono font-bold">3.</span>
                <span>非活动组织者与无安全保障义务（《民法典》第 1198 条）</span>
              </h4>
              <p class="text-gray-300">
                本软件为个人开源之非营利性数字向导工具，开发者既非旅游经营者，亦非户外探险活动之召集人、组织者或领队，不收取任何服务费用。开发者不对任何用户的线下出行行为承担《民法典》第一千一百九十八条规定之经营者或组织者安全保障义务。
              </p>
            </div>

            <div class="space-y-1.5">
              <h4 class="font-bold text-white text-[13px] flex items-center gap-1.5">
                <span class="text-primary font-mono font-bold">4.</span>
                <span>自然保护区合规与森林防火红线</span>
              </h4>
              <p class="text-gray-300">
                出行请严格遵守《中华人民共和国森林法》、《森林防火条例》及自然保护区相关法律规约。进入林区严禁携带火种；严禁擅自违规穿越未经批准开放的自然保护区核心区或开展危险非法黑穿。进山前请通过正规官方渠道向属地林草或文旅部门报备核实开放与管治状态。
              </p>
            </div>

            <div class="space-y-1.5">
              <h4 class="font-bold text-white text-[13px] flex items-center gap-1.5">
                <span class="text-primary font-mono font-bold">5.</span>
                <span>开源许可与责任限制</span>
              </h4>
              <p class="text-gray-300">
                本软件遵循 MIT License 协议依“原样（AS-IS）”免费提供，在法律允许的最大范围内，开发者不对因使用本软件信息、离线数据或第三方地图导航引发的任何直接、间接、意外人身伤亡或财产损失承担损害赔偿或连带连带民事责任。
              </p>
            </div>
          </div>

          <!-- 弹窗底部操作控制栏 -->
          <div class="pt-2 border-t border-white/10 space-y-2.5">
            <!-- 首次强制启动模式下的确认勾选 -->
            <label
              v-if="mandatory"
              class="flex items-start gap-2.5 cursor-pointer text-[11px] text-gray-300 select-none py-1"
            >
              <input
                type="checkbox"
                v-model="hasAgreedCheckbox"
                class="mt-0.5 w-4 h-4 rounded border-white/20 bg-surface-container-high text-primary focus:ring-primary/40 focus:ring-offset-0"
              />
              <span class="leading-snug">
                我已年满 18 周岁，具有完全民事行为能力，已完整阅读并充分知晓上述《户外安全须知与法律免责声明》中的全部风险与法律条款。
              </span>
            </label>

            <div class="flex items-center gap-2">
              <button
                v-if="!mandatory"
                @click="handleClose"
                class="w-full py-2.5 rounded-xl bg-surface-container-high/80 hover:bg-surface-container-high border border-white/10 text-white font-medium text-[13px] active:scale-95 transition-all text-center"
              >
                我已知晓并关闭
              </button>
              <button
                v-else
                @click="handleConfirmAgree"
                :disabled="!hasAgreedCheckbox"
                class="w-full py-3 rounded-xl font-bold text-[13px] flex items-center justify-center gap-1.5 transition-all shadow-lg select-none"
                :class="hasAgreedCheckbox
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 active:scale-95 shadow-[0_0_15px_rgba(78,222,163,0.3)]'
                  : 'bg-surface-container-high/50 border border-white/10 text-gray-500 cursor-not-allowed'"
              >
                <span class="material-symbols-outlined text-[16px]">verified</span>
                <span>同意免责公约并进入应用</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  mandatory: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:modelValue', 'agree']);

const hasAgreedCheckbox = ref(false);

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
});

function onBackdropClick() {
  if (!props.mandatory) {
    handleClose();
  }
}

function handleClose() {
  visible.value = false;
}

function handleConfirmAgree() {
  if (!hasAgreedCheckbox.value) return;
  try {
    localStorage.setItem('alpine_disclaimer_agreed', 'true');
    localStorage.setItem('alpine_disclaimer_agreed_time', new Date().toISOString());
  } catch (e) {
    console.warn('Storage warning:', e);
  }
  emit('agree');
  visible.value = false;
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
