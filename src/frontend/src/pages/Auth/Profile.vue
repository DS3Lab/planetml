<template>
  <div>
    <Disclosure as="div" class="relative overflow-hidden bg-sky-700 pb-32"
      v-slot="{ open }">
      <nav
        :class="[open ? 'bg-sky-900' : 'bg-transparent', 'relative z-10 border-b border-teal-500 border-opacity-25 lg:border-none lg:bg-transparent']">
        <div class="mx-auto max-w-7xl px-2 sm:px-4 lg:px-8">
          <div
            class="relative flex h-16 items-center justify-between lg:border-b lg:border-sky-800">
            <div class="flex items-center px-2 lg:px-0">
              <div class="flex-shrink-0">
                <img class="block h-8 w-auto"
                  src="https://tailwindui.com/img/logos/mark.svg?color=teal&shade=400"
                  alt="Your Company" />
              </div>
              <div class="hidden lg:ml-6 lg:block lg:space-x-4">
                <div class="flex">
                  <a v-for="item in navigation" :key="item.name"
                    :href="item.href"
                    :class="[item.current ? 'bg-black bg-opacity-25' : 'hover:bg-sky-800', 'rounded-md py-2 px-3 text-sm font-medium text-white']">{{
                    item.name }}</a>
                </div>
              </div>
            </div>
            <div class="flex lg:hidden">
              <!-- Mobile menu button -->
              <DisclosureButton
                class="inline-flex items-center justify-center rounded-md p-2 text-sky-200 hover:bg-sky-800 hover:text-white focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white">
                <span class="sr-only">Open main menu</span>
                <Bars3Icon v-if="!open" class="block h-6 w-6 flex-shrink-0"
                  aria-hidden="true" />
                <XMarkIcon v-else class="block h-6 w-6 flex-shrink-0"
                  aria-hidden="true" />
              </DisclosureButton>
            </div>
            <div class="hidden lg:ml-4 lg:block">
              <div class="flex items-center">
                <button type="button"
                  class="flex-shrink-0 rounded-full p-1 text-sky-200 hover:bg-sky-800 hover:text-white focus:bg-sky-900 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-sky-900">
                  <span class="sr-only">View notifications</span>
                  <BellIcon class="h-6 w-6" aria-hidden="true" />
                </button>

                <!-- Profile dropdown -->
                <Menu as="div" class="relative ml-4 flex-shrink-0">
                  <div>
                    <MenuButton
                      class="flex rounded-full text-sm text-white focus:bg-sky-900 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-sky-900">
                      <span class="sr-only">Open user menu</span>
                      <img v-if="is_loaded" class="h-8 w-8 rounded-full"
                        :src="user.photo_url" alt="" />
                    </MenuButton>
                  </div>
                  <transition
                    enter-active-class="transition ease-out duration-100"
                    enter-from-class="transform opacity-0 scale-95"
                    enter-to-class="transform opacity-100 scale-100"
                    leave-active-class="transition ease-in duration-75"
                    leave-from-class="transform opacity-100 scale-100"
                    leave-to-class="transform opacity-0 scale-95">
                    <MenuItems
                      class="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                      <MenuItem v-for="item in userNavigation" :key="item.name"
                        v-slot="{ active }">
                      <a :href="item.href"
                        :class="[active ? 'bg-gray-100' : '', 'block py-2 px-4 text-sm text-gray-700']">{{
                        item.name }}</a>
                      </MenuItem>
                    </MenuItems>
                  </transition>
                </Menu>
              </div>
            </div>
          </div>
        </div>

        <DisclosurePanel class="bg-sky-900 lg:hidden">
          <div class="space-y-1 px-2 pt-2 pb-3">
            <DisclosureButton v-for="item in navigation" :key="item.name" as="a"
              :href="item.href"
              :class="[item.current ? 'bg-black bg-opacity-25' : 'hover:bg-sky-800', 'block rounded-md py-2 px-3 text-base font-medium text-white']">
              {{ item.name }}</DisclosureButton>
          </div>
          <div class="border-t border-sky-800 pt-4 pb-3">
            <div class="flex items-center px-4">
              <div class="flex-shrink-0">
                <img class="h-10 w-10 rounded-full" :src="user.photo_url"
                  alt="" />
              </div>
              <div class="ml-3">
                <div class="text-base font-medium text-white">{{ user.display_name }}
                </div>
                <div class="text-sm font-medium text-sky-200">{{ user.email }}
                </div>
              </div>
              <button type="button"
                class="ml-auto flex-shrink-0 rounded-full p-1 text-sky-200 hover:bg-sky-800 hover:text-white focus:bg-sky-900 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-sky-900">
                <span class="sr-only">View notifications</span>
                <BellIcon class="h-6 w-6" aria-hidden="true" />
              </button>
            </div>
            <div class="mt-3 px-2">
              <DisclosureButton v-for="item in userNavigation" :key="item.name"
                as="a" :href="item.href"
                class="block rounded-md py-2 px-3 text-base font-medium text-sky-200 hover:bg-sky-800 hover:text-white">
                {{ item.name }}</DisclosureButton>
            </div>
          </div>
        </DisclosurePanel>
      </nav>
      <div aria-hidden="true"
        :class="[open ? 'bottom-0' : 'inset-y-0', 'absolute inset-x-0 left-1/2 w-full -translate-x-1/2 transform overflow-hidden lg:inset-y-0']">
        <div class="absolute inset-0 flex">
          <div class="h-full w-1/2" style="background-color: #0a527b" />
          <div class="h-full w-1/2" style="background-color: #065d8c" />
        </div>
        <div class="relative flex justify-center">
          <svg class="flex-shrink-0" width="1750" height="308"
            viewBox="0 0 1750 308" xmlns="http://www.w3.org/2000/svg">
            <path d="M284.161 308H1465.84L875.001 182.413 284.161 308z"
              fill="#0369a1" />
            <path d="M1465.84 308L16.816 0H1750v308h-284.16z" fill="#065d8c" />
            <path d="M1733.19 0L284.161 308H0V0h1733.19z" fill="#0a527b" />
            <path d="M875.001 182.413L1733.19 0H16.816l858.185 182.413z"
              fill="#0a4f76" />
          </svg>
        </div>
      </div>
      <header class="relative py-10">
        <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h1 class="text-3xl font-bold tracking-tight text-white">Settings</h1>
        </div>
      </header>
    </Disclosure>

    <main class="relative -mt-32">
      <div class="mx-auto max-w-screen-xl px-4 pb-6 sm:px-6 lg:px-8 lg:pb-16">
        <div class="overflow-hidden rounded-lg bg-white shadow">
          <div
            class="divide-y divide-gray-200 lg:grid lg:grid-cols-12 lg:divide-y-0 lg:divide-x">

            <form class="divide-y divide-gray-200 lg:col-span-9" action="#"
              method="POST">
              <!-- Profile section -->
              <div v-if="is_loaded" class="py-6 px-4 sm:p-6 lg:pb-8">
                <div>
                  <h2 class="text-lg font-medium leading-6 text-gray-900">
                    Profile</h2>
                  <p class="mt-1 text-sm text-gray-500">This information will be
                    displayed publicly so be careful what you share.</p>
                </div>

                <div  class="mt-6 flex flex-col lg:flex-row">
                  <div class="flex-grow space-y-6">
                    <div>
                      <label for="username"
                        class="block text-sm font-medium text-gray-700">User</label>
                      <div class="mt-1 flex rounded-md shadow-sm">
                        <span
                          class="inline-flex items-center rounded-l-md border border-r-0 border-gray-300 bg-gray-50 px-3 text-gray-500 sm:text-sm">toma_users/</span>
                        <input type="text" name="username" id="username"
                          autocomplete="username" disabled
                          class="block w-full min-w-0 flex-grow rounded-none rounded-r-md border-gray-300 focus:border-sky-500 focus:ring-sky-500 sm:text-sm"
                          :value="user.display_name" />
                      </div>
                    </div>
                  </div>

                  <div
                    class="mt-6 flex-grow lg:mt-0 lg:ml-6 lg:flex-shrink-0 lg:flex-grow-0">
                    <p class="text-sm font-medium text-gray-700"
                      aria-hidden="true">Photo</p>
                    <div class="mt-1 lg:hidden">
                      <div class="flex items-center">
                        <div
                          class="inline-block h-12 w-12 flex-shrink-0 overflow-hidden rounded-full"
                          aria-hidden="true">
                          <img class="h-full w-full rounded-full"
                            :src="user.photo_url" alt="" />
                        </div>
                        <div class="ml-5 rounded-md shadow-sm">
                          <div
                            class="group relative flex items-center justify-center rounded-md border border-gray-300 py-2 px-3 focus-within:ring-2 focus-within:ring-sky-500 focus-within:ring-offset-2 hover:bg-gray-50">
                            <label for="mobile-user-photo"
                              class="pointer-events-none relative text-sm font-medium leading-4 text-gray-700">
                              <span>Change</span>
                              <span class="sr-only"> user photo</span>
                            </label>
                            <input id="mobile-user-photo" name="user-photo"
                              type="file"
                              class="absolute h-full w-full cursor-pointer rounded-md border-gray-300 opacity-0" />
                          </div>
                        </div>
                      </div>
                    </div>

                    <div
                      class="relative hidden overflow-hidden rounded-full lg:block">
                      <img class="relative h-40 w-40 rounded-full"
                        :src="user.photo_url" alt="" />
                    </div>
                  </div>
                </div>

                <div class="mt-6 grid grid-cols-12 gap-6">
                  <div class="col-span-12 sm:col-span-6">
                    <label for="last-name"
                      class="block text-sm font-medium text-gray-700">Access Token</label>
                    <input type="text" name="last-name" id="last-name"
                      autocomplete="family-name" disabled :value="user_access_token"
                      class="mt-1 block w-full rounded-md border border-gray-300 py-2 px-3 shadow-sm focus:border-sky-500 focus:outline-none focus:ring-sky-500 sm:text-sm" />
                  </div>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  Disclosure,
  DisclosureButton,
  DisclosurePanel,
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
} from '@headlessui/vue'
import {
  Bars3Icon,
  BellIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline'
import { getAuth } from 'firebase/auth'
import { getUser } from "@/services/fireuser.js";
import { onMounted } from "vue";

const is_loaded = ref(false);
const user = ref({})
const user_access_token = ref('')
const navigation = [
  { name: 'Home', href: '/', current: false },
  { name: 'Jobs', href: '/jobs', current: false },
  { name: 'Docs', href: 'https://planetml.pages.dev', current: false },
]

const userNavigation = [
  { name: 'Your Profile', href: '#' },
  { name: 'Settings', href: '#' },
  { name: 'Sign out', href: '#' },
]

onMounted(() => {
  getAuth().onAuthStateChanged((response) => {
    if (!response) {
      router.replace({ name: "Login" });
    } else {
      user_access_token.value = response.accessToken
      getUser(response.uid).then((user_data) => {
        user.value = user_data;
        console.log(user.value)
        is_loaded.value = true;
      }).catch((error) => {
        router.replace({ name: "Login" });
      });
    }
  });
})

</script>