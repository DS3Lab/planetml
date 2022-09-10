import { reactive, toRefs } from "vue";
import { getFirestore } from 'firebase/firestore';
import { getAuth } from 'firebase/auth';
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { collection, doc, addDoc, setDoc } from "firebase/firestore"; 

const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    databaseURL: import.meta.env.VITE_FIREBASE_DATABASE_URL,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
};
console.log('initializing firebase')

const fireapp = initializeApp(firebaseConfig)
getAnalytics(fireapp)

const db = getFirestore()
const userCollection = collection(db, 'user_data')

// Add new user data
export const createUser = user => {
    const docRef = doc(db, "user_data", user.user.uid);
    let user_profile = {
        'id': user.user.uid,
        'email': user.user.email,
        'email_verified': user.user.emailVerified,
        'display_name': user.user.displayName,
        'photo_url': user.user.photoURL,
        'last_login': user.user.metadata.lastSignInTime,
        'creation_time': user.user.metadata.creationTime,
        'phone_number': user.user.phoneNumber,
        'provider_id': user.providerId,
    }
    console.log(user_profile)
    return setDoc(docRef, user_profile);
}

// get data
export const getUser = async id => {
    const user = await userCollection.doc(id).get()
    return user.exists ? user.data() : null
}

// update data
export const updateUser = (id, user) => {
    return userCollection.doc(id).update(user)
}

// delete data
export const deleteUser = id => {
    return userCollection.doc(id).delete()
}

export function firebaseUser() {
    const fetchUser = async () => {
        const user = getAuth().currentUser;
        if (user) {
            state.name = user.email;
            state.image = user.photoURL || `https://eu.ui-avatars.com/api/?name=${state.name[0]}&size=1000`
        }
    }

    return {
        ...toRefs(state), // convert to refs when returning
        fetchUser
    }
}


const state = reactive({
    name: "",
    image: ""
});
