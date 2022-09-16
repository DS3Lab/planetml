<template>
  <button
    @click="githubAuth"
    type="button"
    class="transition duration-200 border border-gray-200 text-gray-500 w-full py-2.5 rounded-lg text-sm shadow-sm hover:shadow-md font-normal text-center inline-block"
  >
    Github
  </button>
</template>

<script>
import { getAuth, signInWithPopup, GithubAuthProvider } from "firebase/auth";
import { createUser } from "@/services/fireuser";
import { useRouter } from "vue-router";
export default {
  name: "github-button",

  setup() {
    const router = useRouter();
    function githubAuth() {
      const provider = new GithubAuthProvider();
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

    return { githubAuth };
  },
};
</script>

<style>
</style>