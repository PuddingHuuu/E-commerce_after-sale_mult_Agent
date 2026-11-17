<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { Promotion } from '@element-plus/icons-vue'

const props = withDefaults(
  defineProps<{
    modelValue: string
    disabled?: boolean
    loading?: boolean
    placeholder?: string
    hint?: string
  }>(),
  {
    disabled: false,
    loading: false,
    placeholder: '输入消息…',
    hint: 'Enter 发送 · Shift + Enter 换行',
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
  send: []
}>()

const textarea = ref<HTMLTextAreaElement | null>(null)
const canSend = computed(
  () => props.modelValue.trim().length > 0 && !props.disabled && !props.loading,
)

function resizeTextarea(): void {
  nextTick(() => {
    const element = textarea.value
    if (!element) return
    element.style.height = 'auto'
    element.style.height = `${Math.min(element.scrollHeight, 116)}px`
  })
}

function handleInput(event: Event): void {
  emit('update:modelValue', (event.target as HTMLTextAreaElement).value)
  resizeTextarea()
}

function submit(): void {
  if (!canSend.value) return
  emit('send')
}

function handleKeydown(event: KeyboardEvent): void {
  if (
    event.key === 'Enter' &&
    !event.shiftKey &&
    !event.isComposing
  ) {
    event.preventDefault()
    submit()
  }
}

watch(
  () => props.modelValue,
  () => resizeTextarea(),
)

defineExpose({ focus: () => textarea.value?.focus() })
</script>

<template>
  <div class="composer">
    <div class="composer__box">
      <textarea
        ref="textarea"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        rows="1"
        @input="handleInput"
        @keydown="handleKeydown"
      />
      <div class="composer__actions">
        <span class="composer__hint">{{ hint }}</span>
        <el-button
          class="composer__send"
          type="primary"
          :disabled="!canSend"
          :loading="loading"
          @click="submit"
        >
          发送
          <el-icon v-if="!loading" class="send-icon"><Promotion /></el-icon>
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.composer {
  flex: 0 0 auto;
  padding: 12px 18px 16px;
  border-top: 1px solid #f0f0f4;
  background: #fff;
}

.composer__box {
  padding: 10px 12px 9px;
  border: 1px solid #e6e6ed;
  border-radius: 12px;
  background: #fbfbfd;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    background 0.2s ease;
}

.composer__box:focus-within {
  border-color: color-mix(in srgb, var(--chat-accent, #ff5000) 48%, #ffffff);
  background: #fff;
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--chat-accent, #ff5000) 8%, transparent);
}

.composer textarea {
  display: block;
  width: 100%;
  min-height: 24px;
  max-height: 116px;
  padding: 0;
  border: 0;
  outline: 0;
  color: var(--text);
  background: transparent;
  font-size: 14px;
  line-height: 1.7;
  resize: none;
}

.composer textarea::placeholder {
  color: #b0b0ba;
}

.composer textarea:disabled {
  cursor: not-allowed;
}

.composer__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-top: 6px;
}

.composer__hint {
  font-size: 10px;
  color: #b5b5bd;
}

.composer__send {
  min-width: 82px;
  height: 33px;
  border-radius: 8px;
  font-size: 13px;
}

.send-icon {
  margin-left: 4px;
  font-size: 13px;
}

@media (max-width: 720px) {
  .composer {
    padding: 10px 12px 12px;
  }

  .composer__hint {
    display: none;
  }

  .composer__actions {
    justify-content: flex-end;
  }
}
</style>
