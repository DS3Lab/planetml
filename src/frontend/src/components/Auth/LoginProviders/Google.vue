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
export default {
  name: "google-button",
  setup(props) {
    function googleAuth() {
      const provider = new GoogleAuthProvider();
      provider.addScope('profile');
      provider.addScope('email');

      signInWithPopup(getAuth(), provider)
        .then((res) => {
          console.log(res)
          createUser(res)
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