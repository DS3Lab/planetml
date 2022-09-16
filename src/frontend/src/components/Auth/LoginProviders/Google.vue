<template>
  <div class="google-button">
    <button type="button" @click="googleAuth"
      class="transition duration-200 border border-gray-200 text-gray-500 w-full py-2.5 rounded-lg text-sm shadow-sm hover:shadow-md font-normal text-center inline-block">
      Google
    </button>
  </div>
</template>

<script>
import { getAuth } from "firebase/auth";
import { signInWithPopup, GoogleAuthProvider } from "firebase/auth";
import { createUser } from "@/services/fireuser";
import { useRouter } from "vue-router";
export default {
  name: "google-button",
  setup(props) {
    const router = useRouter();
    function googleAuth() {
      const provider = new GoogleAuthProvider();
      provider.addScope('profile');
      provider.addScope('email');

      signInWithPopup(getAuth(), provider)
        .then((res) => {
          createUser(res)
          router.replace("/profile")
        })
        .catch((error) => {
          console.log(error)
        });
    }
    return { googleAuth };
  },
};
</script>

<style>

</style>