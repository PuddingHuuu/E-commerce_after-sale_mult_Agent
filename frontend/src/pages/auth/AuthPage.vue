<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowRight,
  Check,
  Headset,
  Lock,
  ShoppingBag,
  User,
} from '@element-plus/icons-vue'
import type { Role } from '@/types/api'
import { useAuthStore } from '@/stores/auth'
import { roleMeta } from '@/utils/labels'
import { showError } from '@/api/http'
import RoleRail from '@/components/layout/RoleRail.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const allowedRoles: Role[] = ['consumer', 'platform', 'merchant']
const role = computed<Role>(() => {
  const value = String(route.params.role || 'consumer')
  return allowedRoles.includes(value as Role) ? (value as Role) : 'consumer'
})
const meta = computed(() => roleMeta[role.value])

const mode = ref<'login' | 'register'>('login')
const loading = ref(false)
const remember = ref(true)

const loginForm = reactive({
  login_name: '',
  password: '',
})

const registerForm = reactive({
  display_name: '',
  login_name: '',
  phone: '',
  store_name: '',
  invite_code: '',
  password: '',
  confirm_password: '',
})

const demoAccounts: Record<Role, { login: string; password: string }> = {
  consumer: { login: '13812345678', password: 'Demo1234' },
  platform: { login: 'agent01', password: 'Platform1234' },
  merchant: { login: 'merchant01', password: 'Merchant1234' },
}

const ACCOUNT_KEY_PREFIX = 'orange-after-sale:account:'

function loadRememberedAccount(): void {
  const remembered = window.localStorage.getItem(`${ACCOUNT_KEY_PREFIX}${role.value}`)
  if (remembered && !loginForm.login_name) {
    loginForm.login_name = remembered
  }
}

function rememberAccount(loginName: string): void {
  if (remember.value) {
    window.localStorage.setItem(`${ACCOUNT_KEY_PREFIX}${role.value}`, loginName)
  }
}

const accountLabel = computed(() => {
  if (role.value === 'consumer') return '手机号'
  if (role.value === 'platform') return '员工账号'
  return '商家账号'
})

const roleTitle = computed(() => {
  if (role.value === 'consumer') return '消费者中心'
  if (role.value === 'platform') return '平台客服工作台'
  return '商家协同工作台'
})

const roleDescription = computed(() => {
  if (role.value === 'consumer') {
    return '提交售后申请，查看 AI 处理结果，需要时转人工继续沟通。'
  }
  if (role.value === 'platform') {
    return '统一处理售后工单、订单查询和人工会话，按需邀请商家协同。'
  }
  return '只查看平台邀请你加入的会话，与消费者和平台客服共同处理问题。'
})

const roleIcon = computed(() => {
  if (role.value === 'consumer') return User
  if (role.value === 'platform') return Headset
  return ShoppingBag
})

const features = computed(() => {
  if (role.value === 'consumer') {
    return ['订单按状态分类查看', 'AI 先行处理售后申请', '不满意可转人工继续沟通']
  }
  if (role.value === 'platform') {
    return ['AI 处理中与转人工工单分类', '订单、工单、会话全量搜索', '邀请商家进入人工会话']
  }
  return ['仅显示平台邀请的会话', '消费者、平台、商家三方沟通', '不展示工单与平台内部信息']
})

function redirectTarget(): string {
  const fallback = meta.value.home
  const raw = route.query.redirect
  const candidate = Array.isArray(raw) ? raw[0] : raw
  if (candidate && candidate.startsWith(`/${role.value}/`)) return candidate
  return fallback
}

function redirectHome(): void {
  router.replace(redirectTarget())
}

function resetForms(): void {
  mode.value = 'login'
  loginForm.login_name = ''
  loginForm.password = ''
  Object.assign(registerForm, {
    display_name: '',
    login_name: '',
    phone: '',
    store_name: '',
    invite_code: '',
    password: '',
    confirm_password: '',
  })
}

watch(
  () => role.value,
  () => {
    resetForms()
    loadRememberedAccount()
    if (auth.isLoggedIn(role.value)) redirectHome()
  },
)

onMounted(() => {
  if (!allowedRoles.includes(String(route.params.role) as Role)) {
    router.replace('/auth/consumer')
    return
  }
  if (route.query.expired) {
    ElMessage.warning('登录状态已过期，请重新登录')
  }
  if (auth.isLoggedIn(role.value)) {
    redirectHome()
    return
  }
  loadRememberedAccount()
})

function useDemoAccount(): void {
  mode.value = 'login'
  loginForm.login_name = demoAccounts[role.value].login
  loginForm.password = demoAccounts[role.value].password
}

async function submitLogin(): Promise<void> {
  if (!loginForm.login_name.trim() || !loginForm.password) {
    ElMessage.warning('请输入账号和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(role.value, loginForm.login_name.trim(), loginForm.password, remember.value)
    rememberAccount(loginForm.login_name.trim())
    ElMessage.success('登录成功')
    redirectHome()
  } catch (error) {
    showError(error)
  } finally {
    loading.value = false
  }
}

async function submitRegister(): Promise<void> {
  if (!registerForm.display_name.trim()) {
    ElMessage.warning('请填写显示名称')
    return
  }
  if (!registerForm.login_name.trim()) {
    ElMessage.warning(`请填写${accountLabel.value}`)
    return
  }
  if (role.value === 'merchant' && !registerForm.store_name.trim()) {
    ElMessage.warning('请填写店铺名称')
    return
  }
  if (role.value === 'platform' && !registerForm.invite_code.trim()) {
    ElMessage.warning('请填写平台邀请码')
    return
  }
  if (registerForm.password.length < 8) {
    ElMessage.warning('密码至少需要 8 位')
    return
  }
  if (registerForm.password !== registerForm.confirm_password) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  loading.value = true
  try {
    await auth.register(
      {
        role: role.value,
        login_name: registerForm.login_name.trim(),
        password: registerForm.password,
        display_name: registerForm.display_name.trim(),
        phone:
          role.value === 'consumer'
            ? registerForm.login_name.trim()
            : registerForm.phone.trim() || null,
        store_name: role.value === 'merchant' ? registerForm.store_name.trim() : null,
        invite_code:
          role.value === 'platform' ? registerForm.invite_code.trim() : null,
      },
      remember.value,
    )
    rememberAccount(registerForm.login_name.trim())
    ElMessage.success('注册成功，已自动登录')
    redirectHome()
  } catch (error) {
    showError(error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div
    class="auth-page"
    :class="{ 'auth-page--platform': role === 'platform' }"
    :style="{ '--role-accent': meta.accent }"
  >
    <div class="auth-switch">
      <RoleRail />
    </div>

    <div class="auth-backdrop auth-backdrop--one" />
    <div class="auth-backdrop auth-backdrop--two" />

    <section class="auth-hero">
      <router-link to="/" class="auth-brand">
        <span class="auth-brand__mark"><el-icon><Headset /></el-icon></span>
        <span>
          <strong>橙心售后</strong>
          <small>ORANGE AFTER-SALE</small>
        </span>
      </router-link>

      <div class="auth-hero__main">
        <span class="auth-eyebrow">MULTI-AGENT SERVICE</span>
        <h1>售后问题，<br /><em>分端协同</em>处理</h1>
        <p>
          消费者提交申请，AI 自动完成分类、订单检索与方案回复；不满意再转平台人工，
          必要时由平台邀请商家加入会话。
        </p>

        <div class="auth-role-chip">
          <span class="auth-role-chip__icon">
            <el-icon><component :is="roleIcon" /></el-icon>
          </span>
          <div>
            <strong>{{ roleTitle }}</strong>
            <small>{{ roleDescription }}</small>
          </div>
        </div>

        <ul class="auth-features">
          <li v-for="feature in features" :key="feature">
            <span><el-icon><Check /></el-icon></span>
            {{ feature }}
          </li>
        </ul>
      </div>

      <p class="auth-hero__foot">
        消费者 · 平台客服 · 商家 三个端独立登录，互不越权
      </p>
    </section>

    <section class="auth-card">
      <div class="auth-card__head">
        <div>
          <p class="eyebrow">{{ roleMeta[role].label.toUpperCase() }} ACCESS</p>
          <h2>{{ mode === 'login' ? '登录' : '注册' }}{{ roleMeta[role].label }}账号</h2>
        </div>
        <span class="auth-card__badge">{{ roleMeta[role].label }}</span>
      </div>

      <div class="auth-tabs">
        <button
          type="button"
          :class="{ 'is-active': mode === 'login' }"
          @click="mode = 'login'"
        >
          登录
        </button>
        <button
          type="button"
          :class="{ 'is-active': mode === 'register' }"
          @click="mode = 'register'"
        >
          注册
        </button>
      </div>

      <div v-if="mode === 'login'" class="auth-form">
        <label class="auth-field">
          <span>{{ accountLabel }}</span>
          <el-input
            v-model="loginForm.login_name"
            size="large"
            :prefix-icon="User"
            :placeholder="role === 'consumer' ? '请输入手机号' : '请输入账号'"
            @keyup.enter="submitLogin"
          />
        </label>
        <label class="auth-field">
          <span>密码</span>
          <el-input
            v-model="loginForm.password"
            size="large"
            type="password"
            show-password
            :prefix-icon="Lock"
            placeholder="请输入密码"
            @keyup.enter="submitLogin"
          />
        </label>

        <div class="auth-options">
          <el-checkbox v-model="remember">3 天内免登录</el-checkbox>
          <span>登录状态有效期 72 小时</span>
        </div>

        <el-button
          class="auth-submit"
          type="primary"
          size="large"
          :loading="loading"
          @click="submitLogin"
        >
          登录并进入
          <el-icon><ArrowRight /></el-icon>
        </el-button>

        <div class="demo-hint">
          <div>
            <span>演示账号</span>
            <strong>{{ demoAccounts[role].login }} / {{ demoAccounts[role].password }}</strong>
          </div>
          <button type="button" @click="useDemoAccount">填入</button>
        </div>
      </div>

      <div v-else class="auth-form">
        <div v-if="role === 'merchant'" class="auth-grid">
          <label class="auth-field">
            <span>店铺名称</span>
            <el-input v-model="registerForm.store_name" size="large" placeholder="例如：橙心优选旗舰店" />
          </label>
          <label class="auth-field">
            <span>商家账号</span>
            <el-input v-model="registerForm.login_name" size="large" placeholder="用于登录的账号" />
          </label>
        </div>

        <div v-else class="auth-grid">
          <label class="auth-field">
            <span>{{ role === 'consumer' ? '昵称' : '姓名' }}</span>
            <el-input v-model="registerForm.display_name" size="large" :placeholder="role === 'consumer' ? '例如：林晓' : '例如：客服小橙'" />
          </label>
          <label class="auth-field">
            <span>{{ accountLabel }}</span>
            <el-input
              v-model="registerForm.login_name"
              size="large"
              :placeholder="role === 'consumer' ? '手机号将作为登录账号' : '用于登录的账号'"
            />
          </label>
        </div>

        <div v-if="role === 'merchant'" class="auth-grid">
          <label class="auth-field">
            <span>联系人</span>
            <el-input v-model="registerForm.display_name" size="large" placeholder="联系人姓名" />
          </label>
          <label class="auth-field">
            <span>手机号</span>
            <el-input v-model="registerForm.phone" size="large" placeholder="联系电话" />
          </label>
        </div>

        <label v-if="role === 'platform'" class="auth-field">
          <span>平台邀请码</span>
          <el-input v-model="registerForm.invite_code" size="large" placeholder="请输入平台邀请码" />
        </label>

        <div class="auth-grid">
          <label class="auth-field">
            <span>密码</span>
            <el-input v-model="registerForm.password" size="large" type="password" show-password placeholder="至少 8 位" />
          </label>
          <label class="auth-field">
            <span>确认密码</span>
            <el-input v-model="registerForm.confirm_password" size="large" type="password" show-password placeholder="再次输入密码" />
          </label>
        </div>

        <div class="auth-options">
          <el-checkbox v-model="remember">注册后 3 天内免登录</el-checkbox>
        </div>

        <el-button
          class="auth-submit"
          type="primary"
          size="large"
          :loading="loading"
          @click="submitRegister"
        >
          注册并进入
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>

      <p class="auth-note">
        应用不会保存明文密码，只保存 72 小时有效的登录凭证。
      </p>
    </section>
  </div>
</template>

<style scoped>
.auth-page {
  position: relative;
  display: flex;
  align-items: stretch;
  gap: 48px;
  min-height: 100vh;
  padding: 40px 48px 40px 56px;
  overflow: hidden;
  background:
    radial-gradient(circle at 8% 8%, color-mix(in srgb, var(--role-accent) 12%, transparent), transparent 27%),
    radial-gradient(circle at 92% 88%, rgba(255, 178, 115, 0.12), transparent 24%),
    linear-gradient(135deg, #fcfbfa 0%, #f6f7f9 58%, #f2f3f5 100%);
}

.auth-page--platform {
  background:
    radial-gradient(circle at 8% 8%, rgba(47, 111, 228, 0.12), transparent 27%),
    radial-gradient(circle at 92% 88%, rgba(76, 141, 255, 0.1), transparent 24%),
    linear-gradient(135deg, #fbfcff 0%, #f6f8fd 58%, #f1f4fa 100%);
}

.auth-switch {
  position: absolute;
  z-index: 3;
  top: 22px;
  right: 24px;
}

.auth-page--platform .auth-backdrop--one {
  background: rgba(47, 111, 228, 0.08);
}

.auth-page--platform .auth-backdrop--two {
  background: rgba(76, 141, 255, 0.09);
}

.auth-page--platform .auth-brand__mark {
  background: linear-gradient(145deg, #4c8dff, #2f6fe4);
  box-shadow: 0 8px 18px rgba(47, 111, 228, 0.22);
}

.auth-backdrop {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  filter: blur(2px);
}

.auth-backdrop--one {
  top: -160px;
  left: 30%;
  width: 440px;
  height: 440px;
  background: color-mix(in srgb, var(--role-accent) 7%, transparent);
}

.auth-backdrop--two {
  right: 200px;
  bottom: -180px;
  width: 480px;
  height: 480px;
  background: rgba(255, 190, 139, 0.08);
}

.auth-hero {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  flex: 1;
  min-width: 0;
  padding: 18px 0;
}

.auth-brand {
  display: inline-flex;
  align-items: center;
  gap: 11px;
  width: fit-content;
}

.auth-brand__mark {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 13px;
  color: #fff;
  background: linear-gradient(145deg, #ff8c2f, #ff5000);
  box-shadow: 0 8px 18px rgba(255, 80, 0, 0.22);
  font-size: 21px;
}

.auth-brand > span:last-child {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.auth-brand strong {
  color: #27272c;
  font-size: 17px;
  font-weight: 750;
}

.auth-brand small {
  color: #ababb3;
  font-size: 11px;
  letter-spacing: 0.12em;
}

.auth-hero__main {
  max-width: 610px;
  margin: 50px 0;
}

.auth-eyebrow {
  color: var(--role-accent);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
}

.auth-hero h1 {
  margin-top: 16px;
  color: #202126;
  font-size: clamp(39px, 4vw, 58px);
  font-weight: 750;
  line-height: 1.16;
  letter-spacing: -0.045em;
}

.auth-hero h1 em {
  color: var(--role-accent);
  font-style: normal;
}

.auth-hero__main > p {
  max-width: 560px;
  margin-top: 18px;
  color: #83838e;
  font-size: 14px;
  line-height: 1.9;
}

.auth-role-chip {
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: 560px;
  margin-top: 28px;
  padding: 13px 15px;
  border: 1px solid color-mix(in srgb, var(--role-accent) 13%, #e7e7ec);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.68);
  backdrop-filter: blur(10px);
}

.auth-role-chip__icon {
  display: grid;
  place-items: center;
  flex: 0 0 40px;
  width: 40px;
  height: 40px;
  border-radius: 11px;
  color: #fff;
  background: var(--role-accent);
  font-size: 19px;
}

.auth-role-chip div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.auth-role-chip strong {
  color: #44444c;
  font-size: 13px;
  font-weight: 650;
}

.auth-role-chip small {
  color: #95959e;
  font-size: 13px;
  line-height: 1.55;
}

.auth-features {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  margin-top: 22px;
}

.auth-features li {
  display: flex;
  align-items: center;
  gap: 7px;
  color: #74747e;
  font-size: 13px;
}

.auth-features span {
  display: grid;
  place-items: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  color: var(--role-accent);
  background: color-mix(in srgb, var(--role-accent) 9%, #fff);
  font-size: 12px;
}

.auth-hero__foot {
  color: #b5b5bd;
  font-size: 12px;
  letter-spacing: 0.03em;
}

.auth-card {
  position: relative;
  z-index: 2;
  align-self: center;
  width: min(470px, 100%);
  flex: 0 0 470px;
  padding: 28px 29px 24px;
  border: 1px solid rgba(232, 232, 237, 0.9);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 26px 70px rgba(27, 28, 34, 0.1);
  backdrop-filter: blur(20px);
}

.auth-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.auth-card__head h2 {
  margin-top: 5px;
  color: #2c2c33;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.auth-card__badge {
  padding: 4px 8px;
  border: 1px solid color-mix(in srgb, var(--role-accent) 16%, #fff);
  border-radius: 5px;
  color: var(--role-accent);
  background: color-mix(in srgb, var(--role-accent) 6%, #fff);
  font-size: 12px;
  font-weight: 600;
}

.auth-tabs {
  display: flex;
  gap: 4px;
  margin: 22px 0 20px;
  padding: 3px;
  border-radius: 9px;
  background: #f5f5f7;
}

.auth-tabs button {
  flex: 1;
  height: 38px;
  border-radius: 8px;
  color: #8e8e98;
  background: transparent;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

.auth-tabs button.is-active {
  color: #2d2d33;
  background: #fff;
  box-shadow: 0 2px 8px rgba(24, 24, 28, 0.08);
  font-weight: 600;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.auth-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 11px;
}

.auth-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.auth-field > span {
  color: #74747e;
  font-size: 12px;
  font-weight: 500;
}

.auth-field :deep(.el-input__wrapper) {
  height: 44px;
  border-radius: 9px;
  background: #fbfbfc;
  box-shadow: 0 0 0 1px #e8e8ee inset;
}

.auth-field :deep(.el-input__wrapper.is-focus) {
  background: #fff;
  box-shadow: 0 0 0 1px var(--role-accent) inset !important;
}

.auth-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.auth-options :deep(.el-checkbox__label) {
  color: #74747e;
  font-size: 12px;
}

.auth-options > span {
  color: #b1b1b9;
  font-size: 12px;
}

.auth-submit {
  width: 100%;
  height: 46px;
  margin-top: 2px;
  border-radius: 10px;
  background: var(--role-accent);
  border-color: var(--role-accent);
  font-size: 13px;
  font-weight: 600;
}

.demo-hint {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 11px;
  border: 1px dashed color-mix(in srgb, var(--role-accent) 22%, #e7e7ec);
  border-radius: 9px;
  background: color-mix(in srgb, var(--role-accent) 3.5%, #fff);
}

.demo-hint div {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.demo-hint span {
  color: #a5a5ae;
  font-size: 12px;
}

.demo-hint strong {
  color: #62626c;
  font-family: 'DIN Alternate', 'Bahnschrift', sans-serif;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.02em;
}

.demo-hint button {
  flex: 0 0 auto;
  padding: 6px 10px;
  border: 1px solid color-mix(in srgb, var(--role-accent) 18%, #e5e5eb);
  border-radius: 5px;
  color: var(--role-accent);
  background: #fff;
  font-size: 12px;
  cursor: pointer;
}

.auth-note {
  margin-top: 16px;
  color: #b4b4bb;
  font-size: 12px;
  line-height: 1.6;
  text-align: center;
}

@media (max-width: 1150px) {
  .auth-page {
    gap: 28px;
    padding-right: 32px;
    padding-left: 32px;
  }

  .auth-switch {
    top: 18px;
    right: 18px;
  }

  .auth-hero h1 {
    font-size: 42px;
  }

  .auth-card {
    flex-basis: 430px;
  }
}

@media (max-width: 900px) {
  .auth-page {
    display: block;
    min-height: 100dvh;
    padding: 72px 16px 96px;
  }

  .auth-switch {
    top: 16px;
    right: 16px;
  }

  .auth-hero {
    padding: 0;
  }

  .auth-hero__main {
    margin: 34px 0 24px;
  }

  .auth-hero h1 {
    font-size: 36px;
  }

  .auth-features {
    display: none;
  }

  .auth-hero__foot {
    display: none;
  }

  .auth-card {
    width: 100%;
    margin: 22px 0 0;
    padding: 22px 18px 18px;
    border-radius: 17px;
  }

  .auth-grid {
    grid-template-columns: 1fr;
  }
}
</style>
