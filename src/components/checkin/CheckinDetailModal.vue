<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="visible"
        class="fixed inset-0 z-[120] bg-black/85 backdrop-blur-md flex flex-col items-center justify-end sm:justify-center p-0 sm:p-4"
        @click.self="handleClose"
      >
        <div
          class="w-full max-w-lg max-h-[90vh] bg-[#161a24] border-t sm:border border-white/10 rounded-t-3xl sm:rounded-3xl shadow-2xl flex flex-col overflow-hidden text-on-surface pt-2 pb-[calc(16px+max(env(safe-area-inset-bottom,0px),8px))] px-4 space-y-3 select-none"
        >
          <!-- 弹窗顶栏 -->
          <div class="flex items-center justify-between border-b border-white/10 pb-3 pt-1">
            <div class="flex items-center gap-2 min-w-0">
              <span class="w-2.5 h-2.5 rounded-full bg-primary animate-pulse"></span>
              <h3 class="text-headline-md font-bold text-white text-[16px] truncate">
                {{ mountain?.name }} · 登顶打卡纪实
              </h3>
              <span class="px-2 py-0.5 rounded-md bg-primary/10 text-primary text-[10px] font-mono border border-primary/20 shrink-0">
                {{ mountain?.altitude_m || mountain?.alt }}m
              </span>
            </div>
            <button
              @click="handleClose"
              class="w-8 h-8 rounded-full bg-surface-container-high/80 border border-white/10 hover:border-primary/40 flex items-center justify-center text-on-surface-variant hover:text-white active:scale-95 transition-all"
              aria-label="关闭打卡弹窗"
            >
              <span class="material-symbols-outlined text-[18px]">close</span>
            </button>
          </div>

          <!-- 可滚动内容区 -->
          <div class="flex-1 overflow-y-auto space-y-4 pr-0.5 py-1 text-on-surface">
            <!-- 打卡状态行 -->
            <div class="p-3 rounded-2xl bg-surface-container/60 border border-white/5 flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span
                  class="w-6 h-6 rounded-lg flex items-center justify-center"
                  :class="isMarkedDone ? 'bg-primary/20 text-primary' : 'bg-surface-container-high text-outline'"
                >
                  <span class="material-symbols-outlined text-[16px]">
                    {{ isMarkedDone ? 'check_circle' : 'flag' }}
                  </span>
                </span>
                <span class="text-[13px] font-bold text-white">
                  {{ isMarkedDone ? '已标记为登顶完成' : '尚未登顶打卡' }}
                </span>
              </div>
              <button
                @click="toggleDoneStatus"
                class="px-2.5 py-1 rounded-full text-[11px] font-medium border transition-all active:scale-95"
                :class="isMarkedDone
                  ? 'bg-error/15 border-error/30 text-error hover:bg-error/25'
                  : 'bg-primary/15 border-primary/30 text-primary hover:bg-primary/25'"
              >
                {{ isMarkedDone ? '取消打卡' : '标记已登顶' }}
              </button>
            </div>

            <!-- 照片管理区域 -->
            <div class="space-y-2">
              <div class="flex items-center justify-between text-[12px] font-label-data-sm">
                <span class="flex items-center gap-1.5 text-white font-medium">
                  <span class="material-symbols-outlined text-[15px] text-primary">photo_library</span>
                  实景相册 ({{ draftPhotos.length }}/9 张)
                </span>
                <button
                  v-if="draftPhotos.length < 9"
                  @click="triggerPhotoInput"
                  class="text-primary hover:text-primary/80 font-medium flex items-center gap-0.5 active:scale-95 transition-transform"
                >
                  <span class="material-symbols-outlined text-[14px]">add_a_photo</span>
                  <span>拍照 / 上传相册</span>
                </button>
              </div>

              <!-- 照片九宫格 / 卡片 -->
              <div v-if="draftPhotos.length > 0" class="grid grid-cols-3 gap-2">
                <div
                  v-for="(photo, idx) in draftPhotos"
                  :key="idx"
                  class="aspect-square relative rounded-xl overflow-hidden border border-white/10 bg-black/40 group cursor-pointer"
                  @click="activePreviewIndex = idx; isPreviewLightboxOpen = true"
                >
                  <img :src="photo" :alt="`打卡实景 ${idx + 1}`" class="w-full h-full object-cover" />

                  <!-- 封面标识 -->
                  <span
                    v-if="idx === 0"
                    class="absolute top-1 left-1 px-1 py-0.2 rounded bg-primary/90 text-surface text-[8px] font-bold font-mono shadow-sm"
                  >
                    封面
                  </span>

                  <!-- 操作浮层 -->
                  <div class="absolute inset-0 bg-black/40 opacity-0 sm:group-hover:opacity-100 transition-opacity flex items-center justify-center gap-1">
                    <button
                      v-if="idx > 0"
                      @click.stop="setAsCover(idx)"
                      class="p-1 rounded-md bg-black/70 text-primary text-[10px] hover:bg-primary/20"
                      title="设为封面"
                    >
                      <span class="material-symbols-outlined text-[14px]">star</span>
                    </button>
                    <button
                      @click.stop="removePhoto(idx)"
                      class="p-1 rounded-md bg-black/70 text-error text-[10px] hover:bg-error/20"
                      title="删除"
                    >
                      <span class="material-symbols-outlined text-[14px]">delete</span>
                    </button>
                  </div>

                  <!-- 移动端始终显示的删除按钮 -->
                  <button
                    @click.stop="removePhoto(idx)"
                    class="sm:hidden absolute top-1 right-1 w-5 h-5 rounded-full bg-black/75 text-white/90 flex items-center justify-center text-[12px] active:scale-90"
                  >
                    <span class="material-symbols-outlined text-[12px]">close</span>
                  </button>
                </div>

                <!-- 添加更多网格块 -->
                <div
                  v-if="draftPhotos.length < 9"
                  @click="triggerPhotoInput"
                  class="aspect-square rounded-xl border border-dashed border-white/25 hover:border-primary/50 bg-surface-container-lowest/60 flex flex-col items-center justify-center gap-1 cursor-pointer hover:bg-surface-container-lowest transition-all text-on-surface-variant hover:text-primary active:scale-95"
                >
                  <span class="material-symbols-outlined text-[22px]">add_photo_alternate</span>
                  <span class="font-label-data-sm text-[10px]">+{{ 9 - draftPhotos.length }} 张</span>
                </div>
              </div>

              <!-- 无照片上传引导 -->
              <div
                v-else
                @click="triggerPhotoInput"
                class="w-full py-5 rounded-2xl border border-dashed border-white/20 hover:border-primary/40 bg-surface-container-lowest/60 flex flex-col items-center justify-center gap-1.5 cursor-pointer text-on-surface-variant hover:text-primary transition-all active:scale-98"
              >
                <span class="material-symbols-outlined text-[28px] text-primary/70">add_a_photo</span>
                <span class="text-[12px] font-medium text-white">点击拍照或上传实景相册</span>
                <span class="text-[10px] text-outline">支持相册批量勾选多张照片，单座山最多 9 张 (自动轻量压缩)</span>
              </div>
            </div>

            <!-- 探索心得随笔输入 -->
            <div class="space-y-1.5">
              <div class="flex items-center justify-between text-[12px] font-label-data-sm text-on-surface-variant">
                <span class="flex items-center gap-1 text-white font-medium">
                  <span class="material-symbols-outlined text-[14px] text-secondary">edit_note</span>
                  探索心得与路况随笔
                </span>
                <span class="text-[10px] text-outline">{{ draftNote.length }} / 300 字</span>
              </div>
              <textarea
                v-model="draftNote"
                rows="3"
                maxlength="300"
                placeholder="记录登顶时刻的心情、路况、天气、野生动物或给同行的避坑建议..."
                class="w-full p-3 rounded-2xl bg-surface-container-lowest/90 border border-white/10 text-white text-[12px] font-body-sm focus:outline-none focus:border-primary/50 placeholder:text-outline-variant resize-none"
              ></textarea>
            </div>
          </div>

          <!-- 弹窗底部操作按钮 -->
          <div class="pt-2 border-t border-white/10 flex items-center gap-2">
            <button
              @click="handleClose"
              class="w-1/3 py-2.5 rounded-xl bg-surface-container-high/80 hover:bg-surface-container-high border border-white/10 text-on-surface font-medium text-[13px] active:scale-95 transition-all text-center"
            >
              取消
            </button>
            <button
              @click="handleSave"
              class="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-[13px] flex items-center justify-center gap-1.5 shadow-[0_0_15px_rgba(78,222,163,0.3)] active:scale-95 transition-all"
            >
              <span class="material-symbols-outlined text-[16px]">save</span>
              <span>保存打卡纪实</span>
            </button>
          </div>
        </div>

        <!-- 隐藏的拍照与相册选择 input (支持拍照与相册选择) -->
        <input
          ref="fileInputRef"
          type="file"
          accept="image/*"
          multiple
          class="hidden"
          @change="onFilesSelected"
        />

        <!-- 大图全屏预览 Lightbox -->
        <div
          v-if="isPreviewLightboxOpen"
          class="fixed inset-0 z-[130] bg-black/95 backdrop-blur-md flex flex-col justify-between pt-[calc(14px+max(env(safe-area-inset-top,0px),34px))] pb-[calc(14px+max(env(safe-area-inset-bottom,0px),16px))] px-4"
          @click.self="isPreviewLightboxOpen = false"
        >
          <div class="flex items-center justify-between text-white pb-2">
            <span class="text-[13px] font-mono">
              {{ mountain?.name }} ({{ activePreviewIndex + 1 }} / {{ draftPhotos.length }})
            </span>
            <button
              @click="isPreviewLightboxOpen = false"
              class="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white"
            >
              <span class="material-symbols-outlined text-[18px]">close</span>
            </button>
          </div>

          <div class="flex-1 flex items-center justify-center min-h-0 relative">
            <img
              :src="draftPhotos[activePreviewIndex]"
              :alt="mountain?.name"
              class="max-w-full max-h-full object-contain rounded-xl"
            />
            <button
              v-if="activePreviewIndex > 0"
              @click="activePreviewIndex--"
              class="absolute left-2 w-10 h-10 rounded-full bg-black/60 text-white flex items-center justify-center"
            >
              <span class="material-symbols-outlined">chevron_left</span>
            </button>
            <button
              v-if="activePreviewIndex < draftPhotos.length - 1"
              @click="activePreviewIndex++"
              class="absolute right-2 w-10 h-10 rounded-full bg-black/60 text-white flex items-center justify-center"
            >
              <span class="material-symbols-outlined">chevron_right</span>
            </button>
          </div>

          <div class="flex justify-center gap-3 pt-3 border-t border-white/10">
            <button
              v-if="activePreviewIndex > 0"
              @click="setAsCover(activePreviewIndex); activePreviewIndex = 0"
              class="px-3 py-1.5 rounded-xl bg-primary/20 border border-primary/40 text-primary text-[12px] font-medium"
            >
              设为主封面
            </button>
            <button
              @click="removePhoto(activePreviewIndex); if (draftPhotos.length === 0) isPreviewLightboxOpen = false;"
              class="px-3 py-1.5 rounded-xl bg-error/20 border border-error/40 text-error text-[12px] font-medium"
            >
              删除该照片
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useCheckinStore, compressImageToBase64 } from '@/stores/checkinStore.js';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  mountain: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['update:modelValue', 'saved', 'toast']);

const checkinStore = useCheckinStore();

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
});

const fileInputRef = ref(null);
const isMarkedDone = ref(false);
const draftPhotos = ref([]);
const draftNote = ref('');
const isPreviewLightboxOpen = ref(false);
const activePreviewIndex = ref(0);

// 当弹窗打开或山峰变化时，拉取最新打卡记录填充草稿
watch(
  () => [props.modelValue, props.mountain?.id],
  ([isOpen, mId]) => {
    if (isOpen && mId) {
      isMarkedDone.value = checkinStore.isDone(mId);
      const rec = checkinStore.getCheckinRecord(mId) || {};
      const photos = Array.isArray(rec.photos) && rec.photos.length
        ? [...rec.photos]
        : (rec.photoUrl ? [rec.photoUrl] : []);
      draftPhotos.value = photos;
      draftNote.value = rec.note || '';
    }
  },
  { immediate: true }
);

function toggleDoneStatus() {
  isMarkedDone.value = !isMarkedDone.value;
}

function triggerPhotoInput() {
  if (fileInputRef.value) {
    fileInputRef.value.click();
  }
}

async function onFilesSelected(event) {
  const files = Array.from(event.target.files || []);
  if (!files.length) return;

  const available = 9 - draftPhotos.value.length;
  if (available <= 0) {
    emit('toast', '单座山峰实景相册最多支持 9 张照片');
    event.target.value = '';
    return;
  }

  const toProcess = files.slice(0, available);
  emit('toast', `正在压缩优化 ${toProcess.length} 张照片...`);

  try {
    const compressed = await Promise.all(
      toProcess.map((f) => compressImageToBase64(f, 960, 0.72))
    );
    draftPhotos.value = [...draftPhotos.value, ...compressed];
    // 自动标记登顶
    isMarkedDone.value = true;
    emit('toast', `已成功添加 ${compressed.length} 张实景照片！`);
  } catch (err) {
    console.error('Photo compression error:', err);
    emit('toast', '照片解析失败，请重试');
  } finally {
    event.target.value = '';
  }
}

function removePhoto(idx) {
  draftPhotos.value.splice(idx, 1);
  emit('toast', '已移除该张照片');
}

function setAsCover(idx) {
  if (idx > 0 && idx < draftPhotos.value.length) {
    const [target] = draftPhotos.value.splice(idx, 1);
    draftPhotos.value.unshift(target);
    emit('toast', '已将该照片设为主封面');
  }
}

function handleClose() {
  visible.value = false;
}

function handleSave() {
  if (!props.mountain?.id) return;
  const mId = props.mountain.id;

  if (isMarkedDone.value) {
    // 保存并打卡
    checkinStore.saveCheckinDetail(mId, {
      photos: draftPhotos.value,
      photoUrl: draftPhotos.value[0] || '',
      note: draftNote.value.trim()
    });
    emit('toast', '🎉 登顶打卡与实景纪实保存成功！');
  } else {
    // 取消打卡
    if (checkinStore.isDone(mId)) {
      checkinStore.toggleCheckin(mId);
    }
    emit('toast', '已更新打卡状态');
  }

  emit('saved', mId);
  visible.value = false;
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
