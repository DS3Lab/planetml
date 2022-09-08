<template>
    <div class="min-h-full">
        <main>
            <!-- Page header -->
            <div
                class="mx-auto max-w-3xl px-4 sm:px-6 md:flex md:items-center md:justify-between md:space-x-5 lg:max-w-7xl lg:px-8">
                <div class="flex items-center space-x-5">
                    <div>
                        <h1 class="text-2xl font-bold text-gray-900 ta-center">
                            Job Report</h1>
                        <p class="text-sm font-medium text-gray-500">ID
                            <a href="#" class="text-gray-900">{{job_id}}</a> on
                            <time datetime="2020-08-25">{{created_at}}</time>
                        </p>
                    </div>
                </div>
            </div>

            <div
                class="mx-auto mt-8 grid max-w-3xl grid-cols-1 gap-6 sm:px-6 lg:max-w-7xl lg:grid-flow-col-dense lg:grid-cols-3">
                <div class="space-y-6 lg:col-span-2 lg:col-start-1">
                    <!-- Description list-->
                    <section aria-labelledby="applicant-information-title">
                        <div class="bg-white sm:rounded-lg">
                            <div class="px-4 py-5 sm:px-6">
                                <h2 id="applicant-information-title"
                                    class="text-lg font-medium leading-6 text-gray-900">
                                    Job Information</h2>
                                <p class="mt-1 max-w-2xl text-sm text-gray-500">
                                    All Information about the Job</p>
                            </div>
                            <div
                                class="border-t border-gray-200 px-4 py-5 sm:px-6">
                                <dl
                                    class="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2">
                                    <div class="sm:col-span-1">
                                        <dt
                                            class="text-sm font-medium text-gray-500">
                                            ID</dt>
                                        <dd class="mt-1 text-sm text-gray-900">
                                            {{job_id}}</dd>
                                    </div>
                                    <div class="sm:col-span-1">
                                        <dt
                                            class="text-sm font-medium text-gray-500">
                                            Status</dt>
                                        <dd class="mt-1 text-sm text-gray-900">
                                            {{job_status}}</dd>
                                    </div>
                                    <div class="sm:col-span-1">
                                        <dt
                                            class="text-sm font-medium text-gray-500">
                                            CreatedAt</dt>
                                        <dd class="mt-1 text-sm text-gray-900">
                                            {{created_at}}</dd>
                                    </div>
                                    <div class="sm:col-span-1">
                                        <dt
                                            class="text-sm font-medium text-gray-500">
                                            Source</dt>
                                        <dd class="mt-1 text-sm text-gray-900">
                                            {{source}}</dd>
                                    </div>
                                    <div class="sm:col-span-1">
                                        <dt
                                            class="text-sm font-medium text-gray-500">
                                            Type</dt>
                                        <dd class="mt-1 text-sm text-gray-900">
                                            {{type}}</dd>
                                    </div>
                                    <div class="sm:col-span-1">
                                        <dt
                                            class="text-sm font-medium text-gray-500">
                                            Processed By</dt>
                                        <dd class="mt-1 text-sm text-gray-900">
                                            {{processed_by}}</dd>
                                    </div>
                                    <div class="sm:col-span-2">
                                        <dt
                                            class="text-sm font-medium text-gray-500">
                                            Input</dt>
                                        <dd class="mt-1 text-sm text-gray-900">
                                            {{ request_json }}</dd>
                                    </div>
                                    <div class="sm:col-span-2">
                                        <dt
                                            class="text-sm font-medium text-gray-500">
                                            Attachments</dt>
                                        <dd class="mt-1 text-sm text-gray-900">
                                            <ul role="list"
                                                class="divide-y divide-gray-200 rounded-md border border-gray-200">
                                                <li v-for="attachment in attachments"
                                                    :key="attachment.name"
                                                    class="flex items-center justify-between py-3 pl-3 pr-4 text-sm">
                                                    <div
                                                        class="flex w-0 flex-1 items-center">
                                                        <PaperClipIcon
                                                            class="h-5 w-5 flex-shrink-0 text-gray-400"
                                                            aria-hidden="true" />
                                                        <span
                                                            class="ml-2 w-0 flex-1 truncate">{{
                                                            attachment.name
                                                            }}</span>
                                                    </div>
                                                    <div
                                                        class="ml-4 flex-shrink-0">
                                                        <a :href="attachment.href"
                                                            class="font-medium text-blue-600 hover:text-blue-500">Download</a>
                                                    </div>
                                                </li>
                                            </ul>
                                        </dd>
                                    </div>
                                </dl>
                            </div>
                            <div>
                                <a href="#"
                                    class="block bg-gray-50 px-4 py-4 text-center text-sm font-medium text-gray-500 hover:text-gray-700 sm:rounded-b-lg">Read
                                    full application</a>
                            </div>
                        </div>
                    </section>

                    <!-- Comments-->
                    <section aria-labelledby="notes-title">
                        <div class="bg-white sm:overflow-hidden sm:rounded-lg">
                            <div class="divide-y divide-gray-200">
                                <div class="px-4 py-5 sm:px-6">
                                    <h2 id="notes-title"
                                        class="text-lg font-medium text-gray-900">
                                        Notes</h2>
                                </div>
                                <div class="px-4 py-6 sm:px-6">
                                    <ul role="list" class="space-y-8">
                                        <li v-for="comment in comments"
                                            :key="comment.id">
                                            <div class="flex space-x-3">
                                                <div class="flex-shrink-0">
                                                    <img class="h-10 w-10 rounded-full"
                                                        :src="`https://images.unsplash.com/photo-${comment.imageId}?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80`"
                                                        alt="" />
                                                </div>
                                                <div>
                                                    <div class="text-sm">
                                                        <a href="#"
                                                            class="font-medium text-gray-900">{{
                                                            comment.name }}</a>
                                                    </div>
                                                    <div
                                                        class="mt-1 text-sm text-gray-700">
                                                        <p>{{ comment.body }}
                                                        </p>
                                                    </div>
                                                    <div
                                                        class="mt-2 space-x-2 text-sm">
                                                        <span
                                                            class="font-medium text-gray-500">{{
                                                            comment.date
                                                            }}</span>
                                                        {{ ' ' }}
                                                        <span
                                                            class="font-medium text-gray-500">&middot;</span>
                                                        {{ ' ' }}
                                                        <button type="button"
                                                            class="font-medium text-gray-900">Reply</button>
                                                    </div>
                                                </div>
                                            </div>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                            <div class="bg-gray-50 px-4 py-6 sm:px-6">
                                <div class="flex space-x-3">
                                    <div class="flex-shrink-0">
                                        <img class="h-10 w-10 rounded-full"
                                            :src="user.imageUrl" alt="" />
                                    </div>
                                    <div class="min-w-0 flex-1">
                                        <form action="#">
                                            <div>
                                                <label for="comment"
                                                    class="sr-only">About</label>
                                                <textarea id="comment"
                                                    name="comment" rows="3"
                                                    class="block w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                                    placeholder="Add a note" />
                                            </div>
                                            <div
                                                class="mt-3 flex items-center justify-between">
                                                <a href="#"
                                                    class="group inline-flex items-start space-x-2 text-sm text-gray-500 hover:text-gray-900">
                                                    <QuestionMarkCircleIcon
                                                        class="h-5 w-5 flex-shrink-0 text-gray-400 group-hover:text-gray-500"
                                                        aria-hidden="true" />
                                                    <span>Some HTML is
                                                        okay.</span>
                                                </a>
                                                <button type="submit"
                                                    class="inline-flex items-center justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">Comment</button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
                </div>

                <section aria-labelledby="timeline-title"
                    class="lg:col-span-1 lg:col-start-3">
                    <div class="bg-white px-4 py-5 sm:rounded-lg sm:px-6">
                        <h2 id="timeline-title"
                            class="text-lg font-medium text-gray-900">Timeline
                        </h2>

                        <!-- Activity Feed -->
                        <div class="mt-6 flow-root">
                            <ul role="list" class="-mb-8">
                                <li v-for="(item, itemIdx) in timeline"
                                    :key="item.id">
                                    <div class="relative pb-8">
                                        <span
                                            v-if="itemIdx !== timeline.length - 1"
                                            class="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                                            aria-hidden="true" />
                                        <div class="relative flex space-x-3">
                                            <div>
                                                <span
                                                    :class="[item.type.bgColorClass, 'h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white']">
                                                    <component
                                                        :is="item.type.icon"
                                                        class="h-5 w-5 text-white"
                                                        aria-hidden="true" />
                                                </span>
                                            </div>
                                            <div
                                                class="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                                                <div>
                                                    <p
                                                        class="text-sm text-gray-500">
                                                        {{ item.content }} <a
                                                            href="#"
                                                            class="font-medium text-gray-900">{{
                                                            item.target }}</a>
                                                    </p>
                                                </div>
                                                <div
                                                    class="whitespace-nowrap text-right text-sm text-gray-500">
                                                    <time
                                                        :datetime="item.datetime">{{
                                                        item.date }}</time>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </li>
                            </ul>
                        </div>
                    </div>
                </section>
            </div>
        </main>
    </div>
</template>
  
<script setup>
import { onMounted } from 'vue';
import { get_job_status } from '../services/api'
import { ref } from 'vue'
import VueJsonPretty from 'vue-json-pretty';
import 'vue-json-pretty/lib/styles.css';
import { useRoute } from 'vue-router';
import { highlight, languages } from 'prismjs/components/prism-core';
import { PaperClipIcon } from '@heroicons/vue/20/solid'
import {
    Menu,
    MenuButton,
    MenuItem,
    MenuItems,
    Popover,
    PopoverButton,
    PopoverOverlay,
    PopoverPanel,
    TransitionChild,
    TransitionRoot,
} from '@headlessui/vue'
import {
    ArrowLongLeftIcon,
    CheckIcon,
    HandThumbUpIcon,
    HomeIcon,
    MagnifyingGlassIcon,
    QuestionMarkCircleIcon,
    UserIcon,
} from '@heroicons/vue/20/solid'
import { Bars3Icon, BellIcon, XMarkIcon } from '@heroicons/vue/24/outline'

let job_status = ref("")
let job_id = ref("")
let request_json = ref("")
let created_at = ref("")
let source = ref("")
let type = ref("")
let download = ref("")
let output = ref("")
let returned_payload = ref("{}")
let outputs = ref([])
let rendered_finished = false // only render finished job once
const headers = [
    { text: "ID", value: "id" },
    { text: "Source", value: "source" },
    { text: "Type", value: "type", sortable: true },
    { text: "Status", value: "status", sortable: true }
];
function update_job_status() {
    if (rendered_finished == true) { // this means that the job has finished, and we rendered it already
        return
    }
    get_job_status(job_id.value).then((response) => {
        if (response.data.status == "finished") {
            rendered_finished = true
        }
        console.log(returned_payload)
        job_status.value = response.data.status
        request_json.value = JSON.stringify(response.data.payload, null, 4)
        created_at.value = response.data.created_at
        source.value = response.data.source
        type.value = response.data.type
        if ('result' in response.data.returned_payload) {
            returned_payload.value = response.data.returned_payload['result'].map(function (res) {
                return res['result']['choices'][0]['text']
            })[0]
        }
        download.value = `https://planetd.shift.ml/job/${job_id.value}`
        outputs.value = []
        let nimg = 0
        //for (const trial_id in response.data.returned_payload.output){
        let trial_id = 0
        for (const prompt_id in response.data.returned_payload.output[trial_id]) {
            nimg = nimg + 1;
            outputs.value.push(response.data.returned_payload.output[trial_id][prompt_id])
            if (nimg > 500) {
                break
            }
        }
    });
}
onMounted(() => {
    job_id.value = useRoute().params.jobid;
    update_job_status()
    setInterval(() => {
        update_job_status()
    }, 10000)
})

function highlighter(code) {
    return highlight(code, languages.json);
}
const user = {


    name: 'Whitney Francis',
    email: 'whitney@example.com',
    imageUrl:
        'https://images.unsplash.com/photo-1517365830460-955ce3ccd263?ixlib=rb-=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=8&w=256&h=256&q=80',
}
const navigation = [


    { name: 'Dashboard', href: '#' },
    { name: 'Jobs', href: '#' },
    { name: 'Applicants', href: '#' },
    { name: 'Company', href: '#' },
]
const breadcrumbs = [


    { name: 'Jobs', href: '#', current: false },
    { name: 'Front End Developer', href: '#', current: false },
    { name: 'Applicants', href: '#', current: true },
]
const userNavigation = [


    { name: 'Your Profile', href: '#' },
    { name: 'Settings', href: '#' },
    { name: 'Sign out', href: '#' },
]
const attachments = [


    { name: 'resume_front_end_developer.pdf', href: '#' },
    { name: 'coverletter_front_end_developer.pdf', href: '#' },
]
const eventTypes = {


    applied: { icon: UserIcon, bgColorClass: 'bg-gray-400' },
    advanced: { icon: HandThumbUpIcon, bgColorClass: 'bg-blue-500' },
    completed: { icon: CheckIcon, bgColorClass: 'bg-green-500' },
}
const timeline = [


    {
        id: 1,
        type: eventTypes.applied,
        content: 'Applied to',
        target: 'Front End Developer',
        date: 'Sep 20',
        datetime: '2020-09-20',
    },
    {
        id: 2,
        type: eventTypes.advanced,
        content: 'Advanced to phone screening by',
        target: 'Bethany Blake',
        date: 'Sep 22',
        datetime: '2020-09-22',
    },
    {
        id: 3,
        type: eventTypes.completed,
        content: 'Completed phone screening with',
        target: 'Martha Gardner',
        date: 'Sep 28',
        datetime: '2020-09-28',
    },
    {
        id: 4,
        type: eventTypes.advanced,
        content: 'Advanced to interview by',
        target: 'Bethany Blake',
        date: 'Sep 30',
        datetime: '2020-09-30',
    },
    {
        id: 5,
        type: eventTypes.completed,
        content: 'Completed interview with',
        target: 'Katherine Snyder',
        date: 'Oct 4',
        datetime: '2020-10-04',
    },
]
const comments = [


    {
        id: 1,
        name: 'Leslie Alexander',
        date: '4d ago',
        imageId: '1494790108377-be9c29b29330',
        body: 'Ducimus quas delectus ad maxime totam doloribus reiciendis ex. Tempore dolorem maiores. Similique voluptatibus tempore non ut.',
    },
    {
        id: 2,
        name: 'Michael Foster',
        date: '4d ago',
        imageId: '1519244703995-f4e0f30006d5',
        body: 'Et ut autem. Voluptatem eum dolores sint necessitatibus quos. Quis eum qui dolorem accusantium voluptas voluptatem ipsum. Quo facere iusto quia accusamus veniam id explicabo et aut.',
    },
    {
        id: 3,
        name: 'Dries Vincent',
        date: '4d ago',
        imageId: '1506794778202-cad84cf45f1d',
        body: 'Expedita consequatur sit ea voluptas quo ipsam recusandae. Ab sint et voluptatem repudiandae voluptatem et eveniet. Nihil quas consequatur autem. Perferendis rerum et.',
    },
]

</script>

<style>
.ta-center {
    text-align: center;
}
</style>