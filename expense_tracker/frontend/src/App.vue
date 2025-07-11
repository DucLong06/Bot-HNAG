<template>
	<v-app>
		<v-app-bar app color="primary" dark elevation="2">
			<v-app-bar-title class="font-weight-bold">
				<v-icon class="mr-2">mdi-calculator-variant</v-icon>
				Expense Tracker
			</v-app-bar-title>

			<v-spacer></v-spacer>

			<v-btn to="/" variant="text" class="mr-2">
				<v-icon left>mdi-home</v-icon>
				Trang chủ
			</v-btn>

			<template v-if="authStore.isAuthenticated">
				<v-btn to="/members" variant="text" class="mr-2">
					<v-icon left>mdi-account-group</v-icon>
					Thành viên
				</v-btn>
				<v-btn to="/expenses" variant="text" class="mr-2">
					<v-icon left>mdi-credit-card</v-icon>
					Chi tiêu
				</v-btn>
				<v-btn @click="logout" variant="text" class="mr-2">
					<v-icon left>mdi-logout</v-icon>
					Đăng xuất
				</v-btn>
			</template>
			<template v-else>
				<v-btn to="/login" variant="text">
					<v-icon left>mdi-login</v-icon>
					Đăng nhập
				</v-btn>
			</template>
		</v-app-bar>

		<v-main>
			<v-container class="py-8 px-6" fluid>
				<router-view />
			</v-container>
		</v-main>

		<v-footer app color="grey-lighten-1" class="text-center">
			<div>
				&copy; {{ new Date().getFullYear() }} Expense Tracker. Made with
				❤️ using Vue + Django
			</div>
		</v-footer>
	</v-app>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useAuthStore } from "./stores/auth";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

const logout = async () => {
	await authStore.logout();
	router.push("/");
};

onMounted(() => {
	authStore.checkAuth();
});
</script>

<style scoped>
.v-app-bar-title {
	font-size: 1.25rem !important;
}
</style>
