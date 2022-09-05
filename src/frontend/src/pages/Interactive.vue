<script setup>
import { reactive } from "vue";
import { useMainStore } from "@/stores/main";
import {
    mdiAccount,
    mdiMail,
} from "@mdi/js";
import SectionMain from "@/components/SectionMain.vue";
import CardBox from "@/components/CardBox.vue";
import FormField from "@/components/FormField.vue";
import FormControl from "@/components/FormControl.vue";
import BaseButton from "@/components/BaseButton.vue";
import BaseButtons from "@/components/BaseButtons.vue";
import CodeEditor from 'simple-code-editor';

const mainStore = useMainStore();
const requestForm = reactive({
    request_json: mainStore.request_json,
});

requestForm.request_json = {}

const submitPass = () => {
    //
};
</script>
    
    <template>
    <SectionMain>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CardBox>
                <FormField label="Prompt" help="Required. Your Prompt">

                    <CodeEditor></CodeEditor>

                </FormField>

                <template #footer>
                    <BaseButtons>
                        <BaseButton color="info" type="submit" label="Submit" />
                    </BaseButtons>
                </template>
            </CardBox>

            <CardBox is-form @submit.prevent="submitPass">
                Progress
            </CardBox>
        </div>
    </SectionMain>
</template>