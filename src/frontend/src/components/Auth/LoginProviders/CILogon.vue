<template>
  <button @click="CILogonAuth" type="button"
    class="transition duration-200 border border-gray-200 text-gray-500 w-full py-2.5 rounded-lg text-sm shadow-sm hover:shadow-md font-normal text-center inline-block">
    CILogon
  </button>
</template>

<script>
import { getAuth, signInWithPopup, OAuthProvider } from "firebase/auth";
import { createUser } from "@/services/fireuser";
import { useRouter } from "vue-router";
export default {
  name: "ciLogin-button",

  setup() {
    const router = useRouter();
    function CILogonAuth() {
      const provider = new OAuthProvider('oidc.cilogon');
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

    return { CILogonAuth };
  },
};
</script>

<style>

</style>