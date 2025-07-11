<template>
	<div class="flex justify-center items-center min-h-[60vh]">
		<v-card width="400" elevation="8" class="pa-6">
			<div class="text-center mb-6">
				<v-icon size="48" color="primary">mdi-account-circle</v-icon>
				<h2 class="text-2xl font-bold mt-2">Đăng nhập</h2>
				<p class="text-gray-600">Đăng nhập để quản lý chi tiêu</p>
			</div>

			<v-form @submit.prevent="handleLogin" ref="form">
				<v-text-field
					v-model="username"
					label="Tên đăng nhập"
					variant="outlined"
					required
					:rules="[(v) => !!v || 'Tên đăng nhập là bắt buộc']"
					class="mb-3"
					prepend-inner-icon="mdi-account"
				></v-text-field>

				<v-text-field
					v-model="password"
					label="Mật khẩu"
					type="password"
					variant="outlined"
					required
					:rules="[(v) => !!v || 'Mật khẩu là bắt buộc']"
					class="mb-3"
					prepend-inner-icon="mdi-lock"
				></v-text-field>

				<v-alert v-if="error" type="error" class="mb-4">
					{{ error }}
				</v-alert>

				<v-btn
					type="submit"
					color="primary"
					block
					:loading="authStore.loading"
					size="large"
					class="mb-3"
				>
					<v-icon left>mdi-login</v-icon>
					Đăng nhập
				</v-btn>

				<div class="text-center">
					<p class="text-sm text-gray-600">
						Sử dụng tài khoản superuser để đăng nhập
					</p>
				</div>
			</v-form>
		</v-card>
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

const handleLogin = async () => {
	error.value = "";

	try {
		const success = await authStore.login(username.value, password.value);
		if (success) {
			router.push("/");
		} else {
			error.value = "Tên đăng nhập hoặc mật khẩu không đúng";
		}
	} catch (err: any) {
		error.value = "Có lỗi xảy ra khi đăng nhập";
		console.error("Login error:", err);
	}
};
</script>
