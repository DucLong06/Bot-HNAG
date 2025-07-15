<template>
	<div class="login-container">
		<div class="login-background">
			<div class="bg-shapes">
				<div class="shape shape-1"></div>
				<div class="shape shape-2"></div>
				<div class="shape shape-3"></div>
			</div>
		</div>

		<v-container class="login-content">
			<v-row justify="center" align="center" class="min-h-screen">
				<v-col cols="12" sm="8" md="6" lg="4">
					<v-card class="login-card pa-8" rounded="xl" elevation="0">
						<!-- Header -->
						<div class="login-header text-center mb-8">
							<div class="login-icon mb-6">
								<div class="icon-container">
									<v-icon size="48" class="main-icon"
										>mdi-account-circle</v-icon
									>
									<div class="icon-glow"></div>
								</div>
							</div>
							<h1 class="login-title text-3xl font-bold mb-2">
								Chào mừng trở lại
							</h1>
							<p class="login-subtitle">
								Đăng nhập để tiếp tục quản lý chi tiêu của bạn
							</p>
						</div>

						<!-- Login Form -->
						<v-form
							@submit.prevent="handleLogin"
							ref="form"
							class="login-form"
						>
							<div class="form-group mb-6">
								<label class="form-label">Tên đăng nhập</label>
								<v-text-field
									v-model="username"
									variant="outlined"
									required
									:rules="[
										(v) =>
											!!v || 'Tên đăng nhập là bắt buộc',
									]"
									class="form-input"
									hide-details="auto"
									rounded="lg"
								>
									<template v-slot:prepend-inner>
										<v-icon color="primary"
											>mdi-account</v-icon
										>
									</template>
								</v-text-field>
							</div>

							<div class="form-group mb-6">
								<label class="form-label">Mật khẩu</label>
								<v-text-field
									v-model="password"
									:type="showPassword ? 'text' : 'password'"
									variant="outlined"
									required
									:rules="[
										(v) => !!v || 'Mật khẩu là bắt buộc',
									]"
									class="form-input"
									hide-details="auto"
									rounded="lg"
								>
									<template v-slot:prepend-inner>
										<v-icon color="primary"
											>mdi-lock</v-icon
										>
									</template>
									<template v-slot:append-inner>
										<v-btn
											@click="
												showPassword = !showPassword
											"
											icon
											variant="text"
											size="small"
											class="password-toggle"
										>
											<v-icon size="20">
												{{
													showPassword
														? "mdi-eye-off"
														: "mdi-eye"
												}}
											</v-icon>
										</v-btn>
									</template>
								</v-text-field>
							</div>

							<!-- Error Alert -->
							<v-expand-transition>
								<v-alert
									v-if="error"
									type="error"
									class="mb-6"
									rounded="lg"
									border="start"
									variant="tonal"
								>
									<template v-slot:prepend>
										<v-icon>mdi-alert-circle</v-icon>
									</template>
									{{ error }}
								</v-alert>
							</v-expand-transition>

							<!-- Login Button -->
							<v-btn
								type="submit"
								color="primary"
								variant="elevated"
								block
								:loading="authStore.loading"
								size="large"
								rounded="xl"
								class="login-btn mb-6"
							>
								<template v-slot:prepend>
									<v-icon>mdi-login</v-icon>
								</template>
								Đăng nhập
							</v-btn>

							<!-- Info -->
							<div class="login-info text-center">
								<v-card
									variant="tonal"
									color="info"
									class="pa-4"
									rounded="lg"
								>
									<div class="d-flex align-center">
										<v-icon color="info" class="mr-3"
											>mdi-information</v-icon
										>
										<div class="text-left">
											<div class="font-medium text-sm">
												Thông tin đăng nhập
											</div>
											<div class="text-xs text-info mt-1">
												Sử dụng tài khoản superuser để
												truy cập
											</div>
										</div>
									</div>
								</v-card>
							</div>
						</v-form>
					</v-card>
				</v-col>
			</v-row>
		</v-container>
	</div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const username = ref("");
const password = ref("");
const error = ref("");
const showPassword = ref(false);

const handleLogin = async () => {
	error.value = "";

	try {
		const success = await authStore.login(username.value, password.value);
		if (success) {
			// Show success notification
			if (
				typeof window !== "undefined" &&
				(window as any).showNotification
			) {
				(window as any).showNotification(
					"Đăng nhập thành công!",
					"success",
					"mdi-check-circle"
				);
			}
			router.push("/");
		} else {
			error.value = "Tên đăng nhập hoặc mật khẩu không đúng";
		}
	} catch (err: any) {
		error.value = "Có lỗi xảy ra khi đăng nhập. Vui lòng thử lại.";
		console.error("Login error:", err);
	}
};
</script>

<style scoped>
.login-container {
	min-height: 100vh;
	position: relative;
	overflow: hidden;
}

.login-background {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.bg-shapes {
	position: absolute;
	width: 100%;
	height: 100%;
	overflow: hidden;
}

.shape {
	position: absolute;
	border-radius: 50%;
	opacity: 0.1;
	animation: float 6s ease-in-out infinite;
}

.shape-1 {
	width: 300px;
	height: 300px;
	background: white;
	top: -150px;
	right: -150px;
	animation-delay: 0s;
}

.shape-2 {
	width: 200px;
	height: 200px;
	background: white;
	bottom: -100px;
	left: -100px;
	animation-delay: 2s;
}

.shape-3 {
	width: 150px;
	height: 150px;
	background: white;
	top: 50%;
	left: -75px;
	animation-delay: 4s;
}

@keyframes float {
	0%,
	100% {
		transform: translateY(0px) rotate(0deg);
	}
	33% {
		transform: translateY(-20px) rotate(120deg);
	}
	66% {
		transform: translateY(10px) rotate(240deg);
	}
}

.login-content {
	position: relative;
	z-index: 2;
	padding: 2rem 1rem;
}

.login-card {
	background: rgba(255, 255, 255, 0.95);
	backdrop-filter: blur(20px);
	border: 1px solid rgba(255, 255, 255, 0.2);
	box-shadow: 0 20px 40px rgba(102, 126, 234, 0.15);
	transition: transform 0.3s ease;
	animation: slideInUp 0.6s ease-out;
}

@keyframes slideInUp {
	from {
		opacity: 0;
		transform: translateY(30px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

.login-card:hover {
	transform: translateY(-2px);
}

.login-header {
	position: relative;
}

.login-icon {
	position: relative;
	display: inline-block;
}

.icon-container {
	position: relative;
	display: inline-block;
}

.main-icon {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	-webkit-background-clip: text;
	-webkit-text-fill-color: transparent;
	filter: drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3));
}

.icon-glow {
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
	width: 80px;
	height: 80px;
	background: radial-gradient(
		circle,
		rgba(102, 126, 234, 0.2) 0%,
		transparent 70%
	);
	border-radius: 50%;
	animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
	0%,
	100% {
		transform: translate(-50%, -50%) scale(1);
		opacity: 0.5;
	}
	50% {
		transform: translate(-50%, -50%) scale(1.1);
		opacity: 0.8;
	}
}

.login-title {
	background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
	-webkit-background-clip: text;
	-webkit-text-fill-color: transparent;
	line-height: 1.2;
}

.login-subtitle {
	color: rgb(107, 114, 128);
	font-size: 1rem;
	margin-bottom: 0;
}

.login-form {
	width: 100%;
}

.form-group {
	position: relative;
}

.form-label {
	display: block;
	font-weight: 500;
	color: rgb(55, 65, 81);
	margin-bottom: 0.5rem;
	font-size: 0.875rem;
}

.form-input {
	transition: all 0.2s ease;
}

.form-input :deep(.v-field) {
	background: rgba(248, 250, 252, 0.8);
	border-radius: 12px;
	border: 1px solid rgba(102, 126, 234, 0.2);
	transition: all 0.2s ease;
}

.form-input :deep(.v-field--focused) {
	background: rgba(255, 255, 255, 0.9);
	border-color: rgba(102, 126, 234, 0.5);
	box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input :deep(.v-field:hover) {
	border-color: rgba(102, 126, 234, 0.3);
}

.password-toggle {
	border-radius: 8px;
}

.password-toggle:hover {
	background: rgba(102, 126, 234, 0.08);
}

.login-btn {
	font-weight: 600;
	text-transform: none;
	height: 56px;
	font-size: 1rem;
	transition: all 0.2s ease;
	box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
}

.login-btn:hover {
	transform: translateY(-1px);
	box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.login-info {
	margin-top: 1rem;
}

.min-h-screen {
	min-height: 100vh;
}

@media (max-width: 600px) {
	.login-card {
		margin: 1rem;
		padding: 2rem 1.5rem !important;
	}

	.login-title {
		font-size: 1.75rem;
	}

	.shape-1,
	.shape-2,
	.shape-3 {
		display: none;
	}

	.login-content {
		padding: 1rem 0.5rem;
	}

	.form-group {
		margin-bottom: 1rem;
	}
}

@media (max-width: 400px) {
	.login-card {
		padding: 1.5rem 1rem !important;
	}

	.login-title {
		font-size: 1.5rem;
	}

	.login-subtitle {
		font-size: 0.875rem;
	}
}

/* Dark theme adjustments */
.v-theme--dark .login-card {
	background: rgba(30, 41, 59, 0.95);
	border-color: rgba(100, 116, 139, 0.2);
}

.v-theme--dark .form-input :deep(.v-field) {
	background: rgba(51, 65, 85, 0.8);
	border-color: rgba(100, 116, 139, 0.2);
}

.v-theme--dark .form-input :deep(.v-field--focused) {
	background: rgba(51, 65, 85, 0.9);
	border-color: rgba(129, 140, 248, 0.5);
}

.v-theme--dark .form-label {
	color: rgb(203, 213, 225);
}

.v-theme--dark .login-subtitle {
	color: rgb(148, 163, 184);
}

/* Loading state for button */
.login-btn:disabled {
	opacity: 0.7;
	transform: none !important;
}

/* Form validation styles */
.form-input :deep(.v-field--error) {
	border-color: #ff6b6b !important;
	animation: shake 0.3s ease-in-out;
}

@keyframes shake {
	0%,
	100% {
		transform: translateX(0);
	}
	25% {
		transform: translateX(-2px);
	}
	75% {
		transform: translateX(2px);
	}
}

/* Success state (if needed) */
.form-input :deep(.v-field--success) {
	border-color: #51cf66 !important;
}

/* Focus visible for accessibility */
.login-btn:focus-visible {
	outline: 2px solid rgba(102, 126, 234, 0.5);
	outline-offset: 2px;
}

.form-input :deep(.v-field--focused) {
	outline: none;
}

/* Custom scrollbar for this page */
.login-container::-webkit-scrollbar {
	width: 6px;
}

.login-container::-webkit-scrollbar-thumb {
	background: rgba(255, 255, 255, 0.3);
	border-radius: 3px;
}
</style>
