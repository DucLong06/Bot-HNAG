<template>
    <div v-if="expense">
      <v-btn @click="$router.go(-1)" class="mb-4" variant="outlined">
        <v-icon left>mdi-arrow-left</v-icon>
        Quay lại
      </v-btn>
      
      <v-card elevation="3">
        <v-card-title class="bg-primary text-white text-h4">
          <v-icon left size="32">mdi-receipt</v-icon>
          {{ expense.name }}
        </v-card-title>
        
        <v-card-text class="pa-6">
          <v-row>
            <v-col cols="12" md="6">
              <v-card variant="outlined" class="pa-4">
                <h3 class="text-lg font-semibold mb-4 flex items-center">
                  <v-icon class="mr-2" color="primary">mdi-information</v-icon>
                  Thông tin chung
                </h3>
                
                <div class="space-y-3">
                  <div class="flex items-center">
                    <v-icon color="success" class="mr-3">mdi-account-cash</v-icon>
                    <div>
                      <strong>Người trả:</strong>
                      <v-chip color="success" size="small" class="ml-2">
                        {{ expense.payer.name }}
                      </v-chip>
                    </div>
                  </div>
                  
                  <div class="flex items-center">
                    <v-icon color="primary" class="mr-3">mdi-currency-usd</v-icon>
                    <div>
                      <strong>Tổng tiền:</strong>
                      <span class="text-lg font-bold ml-2 text-primary">
                        {{ formatCurrency(expense.total_amount) }}
                      </span>
                    </div>
                  </div>
                  
                  <div class="flex items-center">
                    <v-icon color="orange" class="mr-3">mdi-calendar</v-icon>
                    <div>
                      <strong>Ngày tạo:</strong>
                      <span class="ml-2">{{ formatDate(expense.created_at) }}</span>
                    </div>
                  </div>
                  
                  <div class="flex items-center">
                    <v-icon color="purple" class="mr-3">mdi-account-group</v-icon>
                    <div>
                      <strong>Số người tham gia:</strong>
                      <span class="ml-2">{{ expense.participants.length }}</span>
                    </div>
                  </div>
                </div>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-card variant="outlined" class="pa-4">
                <h3 class="text-lg font-semibold mb-4 flex items-center">
                  <v-icon class="mr-2" color="primary">mdi-account-multiple</v-icon>
                  Người tham gia
                </h3>
                
                <div class="space-y-2">
                  <v-card
                    v-for="participant in expense.participants" 
                    :key="participant.id"
                    variant="outlined"
                    class="pa-3"
                  >
                    <div class="flex justify-between items-center">
                      <div>
                        <div class="font-semibold">{{ participant.member.name }}</div>
                        <div class="text-sm text-gray-600">
                          {{ formatCurrency(participant.amount_owed) }}
                        </div>
                      </div>
                      
                      <div class="flex items-center space-x-2">
                        <v-chip 
                          :color="participant.is_paid ? 'success' : 'error'"
                          size="small"
                        >
                          <v-icon left size="small">
                            {{ participant.is_paid ? 'mdi-check-circle' : 'mdi-clock-outline' }}
                          </v-icon>
                          {{ participant.is_paid ? 'Đã trả' : 'Chưa trả' }}
                        </v-chip>
                        
                        <v-btn 
                          v-if="authStore.isAuthenticated"
                          @click="togglePaid(participant)"
                          size="small"
                          :color="participant.is_paid ? 'error' : 'success'"
                          variant="outlined"
                        >
                          <v-icon size="small">
                            {{ participant.is_paid ? 'mdi-close' : 'mdi-check' }}
                          </v-icon>
                        </v-btn>
                      </div>
                    </div>
                  </v-card>
                </div>
              </v-card>
            </v-col>
          </v-row>
          
          <!-- Summary Statistics -->
          <v-row class="mt-4">
            <v-col cols="12">
              <v-card variant="outlined" class="pa-4">
                <h3 class="text-lg font-semibold mb-4 flex items-center">
                  <v-icon class="mr-2" color="primary">mdi-chart-line</v-icon>
                  Thống kê
                </h3>
                
                <v-row>
                  <v-col cols="6" md="3">
                    <div class="text-center">
                      <div class="text-2xl font-bold text-success">{{ paidCount }}</div>
                      <div class="text-sm text-gray-600">Đã trả</div>
                    </div>
                  </v-col>
                  <v-col cols="6" md="3">
                    <div class="text-center">
                      <div class="text-2xl font-bold text-error">{{ unpaidCount }}</div>
                      <div class="text-sm text-gray-600">Chưa trả</div>
                    </div>
                  </v-col>
                  <v-col cols="6" md="3">
                    <div class="text-center">
                      <div class="text-2xl font-bold text-success">{{ formatCurrency(paidAmount) }}</div>
                      <div class="text-sm text-gray-600">Đã thu</div>
                    </div>
                  </v-col>
                  <v-col cols="6" md="3">
                    <div class="text-center">
                      <div class="text-2xl font-bold text-error">{{ formatCurrency(unpaidAmount) }}</div>
                      <div class="text-sm text-gray-600">Còn nợ</div>
                    </div>
                  </v-col>
                </v-row>
              </v-card>
            </v-col>
          </v-row>
          
          <!-- Telegram reminder buttons for authenticated users -->
          <v-row v-if="authStore.isAuthenticated && unpaidParticipants.length > 0" class="mt-4">
            <v-col cols="12">
              <v-card variant="outlined" class="pa-4">
                <h3 class="text-lg font-semibold mb-4 flex items-center">
                  <v-icon class="mr-2" color="primary">mdi-telegram</v-icon>
                  Gửi nhắc nhở Telegram
                </h3>
                
                <div class="flex flex-wrap gap-2 mb-4">
                  <v-btn 
                    v-for="participant in unpaidParticipants" 
                    :key="participant.id"
                    @click="sendReminder(participant.member.id)"
                    color="orange"
                    variant="outlined"
                    :loading="loading"
                  >
                    <v-icon left>mdi-send</v-icon>
                    Nhắc {{ participant.member.name }}
                  </v-btn>
                </div>
                
                <v-btn 
                  v-if="unpaidParticipants.length > 1"
                  @click="sendBulkReminders"
                  color="red"
                  :loading="loading"
                  block
                >
                  <v-icon left>mdi-send-outline</v-icon>
                  Gửi nhắc nhở cho tất cả ({{ unpaidParticipants.length }} người)
                </v-btn>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
  
      <!-- Snackbar for notifications -->
      <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000">
        {{ snackbarText }}
        <template v-slot:actions>
          <v-btn color="white" variant="text" @click="snackbar = false">
            Đóng
          </v-btn>
        </template>
      </v-snackbar>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'
  import { useRoute } from 'vue-router'
  import { expensesApi, telegramApi } from '../services/api'
  import { useAuthStore } from '../stores/auth'
  
  const route = useRoute()
  const authStore = useAuthStore()
  const expense = ref(null)
  const loading = ref(false)
  const snackbar = ref(false)
  const snackbarText = ref('')
  const snackbarColor = ref('success')
  
  const unpaidParticipants = computed(() => {
    if (!expense.value) return []
    return expense.value.participants.filter((p: any) => !p.is_paid)
  })
  
  const paidCount = computed(() => {
    if (!expense.value) return 0
    return expense.value.participants.filter((p: any) => p.is_paid).length
  })
  
  const unpaidCount = computed(() => {
    if (!expense.value) return 0
    return expense.value.participants.filter((p: any) => !p.is_paid).length
  })
  
  const paidAmount = computed(() => {
    if (!expense.value) return 0
    return expense.value.participants
      .filter((p: any) => p.is_paid)
      .reduce((sum: number, p: any) => sum + p.amount_owed, 0)
  })
  
  const unpaidAmount = computed(() => {
    if (!expense.value) return 0
    return expense.value.participants
      .filter((p: any) => !p.is_paid)
      .reduce((sum: number, p: any) => sum + p.amount_owed, 0)
  })
  
  const fetchExpense = async () => {
    try {
      const response = await expensesApi.get(Number(route.params.id))
      expense.value = response.data
    } catch (error) {
      console.error('Error fetching expense:', error)
    }
  }
  
  const togglePaid = async (participant: any) => {
    try {
      await expensesApi.markPaid(expense.value.id, participant.member.id)
      participant.is_paid = !participant.is_paid
      
      snackbarText.value = `Đã cập nhật trạng thái thanh toán cho ${participant.member.name}`
      snackbarColor.value = 'success'
      snackbar.value = true
    } catch (error) {
      console.error('Error marking paid:', error)
      snackbarText.value = 'Có lỗi khi cập nhật trạng thái'
      snackbarColor.value = 'error'
      snackbar.value = true
    }
  }
  
  const sendReminder = async (memberId: number) => {
    loading.value = true
    try {
      await telegramApi.sendReminder(memberId)
      snackbarText.value = 'Đã gửi nhắc nhở thành công!'
      snackbarColor.value = 'success'
      snackbar.value = true
    } catch (error) {
      console.error('Error sending reminder:', error)
      snackbarText.value = 'Có lỗi khi gửi nhắc nhở'
      snackbarColor.value = 'error'
      snackbar.value = true
    } finally {
      loading.value = false
    }
  }
  
  const sendBulkReminders = async () => {
    const memberIds = unpaidParticipants.value.map((p: any) => p.member.id)
    loading.value = true
    try {
      await telegramApi.sendBulkReminders(memberIds)
      snackbarText.value = `Đã gửi nhắc nhở cho ${memberIds.length} người!`
      snackbarColor.value = 'success'
      snackbar.value = true
    } catch (error) {
      console.error('Error sending bulk reminders:', error)
      snackbarText.value = 'Có lỗi khi gửi nhắc nhở hàng loạt'
      snackbarColor.value = 'error'
      snackbar.value = true
    } finally {
      loading.value = false
    }
  }
  
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(amount)
  }
  
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  onMounted(fetchExpense)
  </script>