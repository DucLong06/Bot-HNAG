<template>
	<v-app>
		<!-- Modern App Bar -->
		<v-app-bar
			app
			flat
			class="app-bar px-4 backdrop-blur-lg border-b border-surface-variant/20"
			height="80"
		>
			<div class="d-flex align-center w-100">
				<!-- Logo & Title -->
				<div class="d-flex align-center">
					<div class="logo-container mr-3">
						<v-icon size="32" class="logo-icon">
							mdi-calculator-variant
						</v-icon>
					</div>
					<div>
						<h1 class="app-title text-xl font-bold">
							ExpenseTracker
						</h1>
						<p class="app-subtitle text-xs text-on-surface-variant">
							Quản lý chi tiêu thông minh
						</p>
					</div>
				</div>

				<v-spacer></v-spacer>

				<!-- Navigation -->
				<div class="d-flex align-center">
					<!-- Home -->
					<v-btn
						to="/"
						variant="text"
						class="nav-btn mx-1"
						rounded="xl"
						:class="{ 'nav-active': $route.path === '/' }"
					>
						<v-icon size="20" class="mr-2">mdi-home</v-icon>
						<span class="hidden-sm-and-down">Trang chủ</span>
					</v-btn>

					<!-- Authenticated Navigation -->
					<template v-if="authStore.isAuthenticated">
						<v-btn
							to="/members"
							variant="text"
							class="nav-btn mx-1"
							rounded="xl"
							:class="{
								'nav-active': $route.path === '/members',
							}"
						>
							<v-icon size="20" class="mr-2"
								>mdi-account-group</v-icon
							>
							<span class="hidden-sm-and-down">Thành viên</span>
						</v-btn>

						<v-btn
							to="/expenses"
							variant="text"
							class="nav-btn mx-1"
							rounded="xl"
							:class="{
								'nav-active':
									$route.path.startsWith('/expenses'),
							}"
						>
							<v-icon size="20" class="mr-2"
								>mdi-credit-card</v-icon
							>
							<span class="hidden-sm-and-down">Chi tiêu</span>
						</v-btn>

						<v-divider
							vertical
							class="mx-3 hidden-sm-and-down"
						></v-divider>

						<!-- User Menu -->
						<v-menu>
							<template v-slot:activator="{ props }">
								<v-btn
									v-bind="props"
									variant="text"
									class="nav-btn user-menu-btn"
									rounded="xl"
								>
									<v-avatar
										size="32"
										class="mr-2"
										color="primary"
									>
										<v-icon color="white"
											>mdi-account-circle</v-icon
										>
									</v-avatar>
									<span class="hidden-sm-and-down"
										>Tài khoản</span
									>
									<v-icon class="ml-1 hidden-sm-and-down"
										>mdi-chevron-down</v-icon
									>
								</v-btn>
							</template>
							<v-list
								class="user-menu pa-2"
								rounded="lg"
								min-width="200"
							>
								<v-list-item
									class="user-info mb-2"
									rounded="lg"
								>
									<template v-slot:prepend>
										<v-avatar color="primary" size="36">
											<v-icon
												color="white"
												v-if="!authStore.user?.username"
												>mdi-account</v-icon
											>
											<span
												v-else
												class="text-white font-weight-bold"
											>
												{{
													authStore.user.username
														.charAt(0)
														.toUpperCase()
												}}
											</span>
										</v-avatar>
									</template>

									<v-list-item-title
										class="font-weight-medium"
									>
										{{
											authStore.user?.username ||
											"Người dùng"
										}}
									</v-list-item-title>

									<v-list-item-subtitle class="text-caption">
										{{
											authStore.user?.is_superuser
												? "Quản trị viên"
												: "Thành viên"
										}}
									</v-list-item-subtitle>
								</v-list-item>
								<v-divider class="my-2"></v-divider>

								<v-list-item
									@click="logout"
									rounded="lg"
									class="logout-item"
								>
									<template v-slot:prepend>
										<v-icon color="error"
											>mdi-logout</v-icon
										>
									</template>
									<v-list-item-title
										>Đăng xuất</v-list-item-title
									>
								</v-list-item>
							</v-list>
						</v-menu>
					</template>

					<!-- Login Button for non-authenticated users -->
					<template v-else>
						<v-btn
							to="/login"
							variant="elevated"
							color="primary"
							rounded="xl"
							class="px-6 login-btn"
						>
							<v-icon size="20" class="mr-2">mdi-login</v-icon>
							<span>Đăng nhập</span>
						</v-btn>
					</template>
				</div>
			</div>
		</v-app-bar>

		<!-- Main Content -->
		<v-main>
			<div class="main-container">
				<v-container fluid class="pa-6">
					<!-- Page Transition -->
					<router-view v-slot="{ Component }">
						<transition name="page" mode="out-in">
							<component :is="Component" />
						</transition>
					</router-view>
				</v-container>
			</div>
		</v-main>

		<!-- Modern Footer -->
		<v-footer app class="footer" height="60">
			<div class="d-flex align-center justify-center w-100">
				<div class="text-center">
					<div class="footer-text text-white text-sm">
						© {{ new Date().getFullYear() }} ExpenseTracker
					</div>
					<div class="footer-subtitle text-white/60 text-xs">
						Made with ❤️ using Vue + Django
					</div>
				</div>
			</div>
		</v-footer>

		<!-- Global Loading Overlay -->
		<v-overlay
			v-model="authStore.loading"
			class="align-center justify-center"
			persistent
		>
			<div class="text-center">
				<v-progress-circular
					color="primary"
					indeterminate
					size="64"
					width="4"
				></v-progress-circular>
				<div class="text-white mt-4 font-weight-medium">
					Đang xử lý...
				</div>
			</div>
		</v-overlay>

		<!-- Global Snackbar for notifications -->
		<v-snackbar
			v-model="notification.show"
			:color="notification.color"
			:timeout="notification.timeout"
			location="top right"
			rounded="lg"
			class="modern-snackbar"
		>
			<div class="d-flex align-center">
				<v-icon class="mr-3">
					{{ notification.icon }}
				</v-icon>
				{{ notification.text }}
			</div>
			<template v-slot:actions>
				<v-btn
					color="white"
					variant="text"
					@click="notification.show = false"
					size="small"
					rounded="lg"
				>
					Đóng
				</v-btn>
			</template>
		</v-snackbar>
	</v-app>
</template>

<script setup lang="ts">
import { onMounted, reactive } from "vue";
import { useAuthStore } from "./stores/auth";
import { useRouter, useRoute } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();

// Global notification system
const notification = reactive({
	show: false,
	text: "",
	color: "success",
	icon: "mdi-check-circle",
	timeout: 4000,
});

// Logout function
const logout = async () => {
	try {
		await authStore.logout();
		notification.text = "Đăng xuất thành công";
		notification.color = "success";
		notification.icon = "mdi-check-circle";
		notification.show = true;
		router.push("/");
	} catch (error) {
		notification.text = "Có lỗi khi đăng xuất";
		notification.color = "error";
		notification.icon = "mdi-alert-circle";
		notification.show = true;
	}
};

// Global notification function
const showNotification = (
	text: string,
	color: string = "success",
	icon: string = "mdi-check-circle"
) => {
	notification.text = text;
	notification.color = color;
	notification.icon = icon;
	notification.show = true;
};

// Check authentication on app mount
onMounted(() => {
	authStore.checkAuth();
});

// Make showNotification available globally
if (typeof window !== "undefined") {
	(window as any).showNotification = showNotification;
}
</script>

<style scoped>
/* App Bar Styles */
.app-bar {
	background: rgba(255, 255, 255, 0.95) !important;
	backdrop-filter: blur(20px);
	border-bottom: 1px solid rgba(102, 126, 234, 0.1);
}

.logo-container {
	position: relative;
	width: 48px;
	height: 48px;
	border-radius: 12px;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
}

.logo-icon {
	color: white;
	filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.app-title {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	-webkit-background-clip: text;
	-webkit-text-fill-color: transparent;
	line-height: 1.2;
}

.app-subtitle {
	margin-top: -2px;
}

/* Navigation Styles */
.nav-btn {
	font-weight: 500 !important;
	transition: all 0.2s ease;
	min-width: auto;
}

.nav-btn:hover {
	background: rgba(102, 126, 234, 0.08) !important;
	transform: translateY(-1px);
}

.nav-active {
	background: rgba(102, 126, 234, 0.12) !important;
	color: rgb(102, 126, 234) !important;
}

.user-menu-btn:hover {
	background: rgba(102, 126, 234, 0.08) !important;
}

.login-btn {
	font-weight: 500;
	text-transform: none;
	box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
}

.login-btn:hover {
	transform: translateY(-1px);
	box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
}

/* User Menu Styles */
.user-menu {
	background: rgba(255, 255, 255, 0.95) !important;
	backdrop-filter: blur(20px);
	border: 1px solid rgba(102, 126, 234, 0.1);
	box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
}

.user-info {
	background: rgba(102, 126, 234, 0.05);
	border: 1px solid rgba(102, 126, 234, 0.1);
}

.logout-item:hover {
	background: rgba(244, 67, 54, 0.08) !important;
}

/* Main Content Styles */
.main-container {
	background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
	min-height: calc(100vh - 140px);
	position: relative;
}

.main-container::before {
	content: "";
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23667eea' fill-opacity='0.02'%3E%3Ccircle cx='30' cy='30' r='1'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")
		repeat;
	pointer-events: none;
}

/* Footer Styles */
.footer {
	background: rgba(15, 23, 42, 0.95) !important;
	backdrop-filter: blur(10px);
	color: white;
}

.footer-text {
	font-weight: 500;
}

/* Page Transitions */
.page-enter-active,
.page-leave-active {
	transition: all 0.3s ease;
}

.page-enter-from {
	opacity: 0;
	transform: translateY(20px);
}

.page-leave-to {
	opacity: 0;
	transform: translateY(-20px);
}

/* Snackbar Styles */
.modern-snackbar {
	backdrop-filter: blur(10px);
}

/* Responsive Design */
@media (max-width: 959px) {
	.hidden-sm-and-down {
		display: none !important;
	}

	.app-title {
		font-size: 1.1rem;
	}

	.logo-container {
		width: 40px;
		height: 40px;
	}

	.nav-btn {
		min-width: 40px;
		padding: 0 8px;
	}
}

@media (max-width: 600px) {
	.app-bar {
		height: 64px !important;
	}

	.main-container {
		min-height: calc(100vh - 124px);
	}

	.logo-container {
		margin-right: 8px !important;
	}

	.app-subtitle {
		display: none;
	}
}

/* Dark mode support */
.v-theme--dark .app-bar {
	background: rgba(30, 41, 59, 0.95) !important;
	border-bottom-color: rgba(102, 126, 234, 0.2);
}

.v-theme--dark .main-container {
	background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

.v-theme--dark .user-menu {
	background: rgba(30, 41, 59, 0.95) !important;
}

/* Global card styles */
:deep(.modern-card) {
	background: rgba(255, 255, 255, 0.9) !important;
	backdrop-filter: blur(10px);
	border: 1px solid rgba(102, 126, 234, 0.1);
	transition: all 0.3s ease;
}

:deep(.modern-card:hover) {
	transform: translateY(-2px);
	box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
}

/* Loading overlay custom styles */
:deep(.v-overlay__content) {
	background: rgba(102, 126, 234, 0.1);
	backdrop-filter: blur(10px);
	border-radius: 16px;
	padding: 2rem;
}
</style>
