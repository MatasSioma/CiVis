<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ROUTE_NAMES } from '@/router/enums/routeNames';
import { getRoleLabel, useAuth } from '@/stores/auth';
import { useToasts } from '@/stores/toasts';
import {
  companyApi,
  jobPostingApi,
  JOB_STATUS_LABELS,
  JOB_TYPE_LABELS,
  type Company,
  type JobPostingListItem,
  type Paginated,
} from '@/services/employer';
const { state } = useAuth();
const router = useRouter();
const { showToast } = useToasts();

const user = computed(() => state.user);

const company = ref<Company | null>(null);
const isCompanyLoading = ref(true);
const isEditingCompany = ref(false);
const isSavingCompany = ref(false);

const companyForm = reactive({
  name: '',
  description: '',
  registration_code: '',
  address: '',
  contact_email: '',
  contact_phone: '',
  website: '',
  date_established: '',
});

const isUserInfoExpanded = ref(false);

function fillCompanyForm(c: Company) {
  companyForm.name = c.name;
  companyForm.description = c.description;
  companyForm.registration_code = c.registration_code;
  companyForm.address = c.address;
  companyForm.contact_email = c.contact_email;
  companyForm.contact_phone = c.contact_phone;
  companyForm.website = c.website;
  companyForm.date_established = c.date_established ?? '';
}

const postings = ref<JobPostingListItem[]>([]);
const postingsPage = ref(1);
const postingsTotal = ref(0);
const postingsNext = ref<string | null>(null);
const postingsPrevious = ref<string | null>(null);
const isPostingsLoading = ref(true);

const totalPages = computed(() => {
  if (postingsTotal.value === 0) {
    return 1;
  }

  return Math.ceil(postingsTotal.value / 10);
});

async function loadCompany() {
  isCompanyLoading.value = true;

  try {
    company.value = await companyApi.mine();

    if (company.value) {
      fillCompanyForm(company.value);
    }
  } catch {
    showToast('Nepavyko įkelti įmonės duomenų.', 'error');
  } finally {
    isCompanyLoading.value = false;
  }
}

async function loadPostings(page: number) {
  isPostingsLoading.value = true;

  try {
    const data: Paginated<JobPostingListItem> = await jobPostingApi.list(page);
    postings.value = data.results;
    postingsTotal.value = data.count;
    postingsNext.value = data.next;
    postingsPrevious.value = data.previous;
    postingsPage.value = page;
  } catch {
    showToast('Nepavyko įkelti skelbimų.', 'error');
  } finally {
    isPostingsLoading.value = false;
  }
}

function startEditCompany() {
  if (!company.value) {
    return;
  }

  fillCompanyForm(company.value);
  isEditingCompany.value = true;
}

function cancelEditCompany() {
  if (company.value) {
    fillCompanyForm(company.value);
  }

  isEditingCompany.value = false;
}

async function saveCompany() {
  if (!company.value) {
    return;
  }

  if (!companyForm.name.trim()) {
    showToast('Įveskite įmonės pavadinimą.', 'error');
    return;
  }

  if (!companyForm.registration_code.trim()) {
    showToast('Įveskite įmonės kodą.', 'error');
    return;
  }

  isSavingCompany.value = true;

  try {
    const updated = await companyApi.update(company.value.id, {
      name: companyForm.name.trim(),
      description: companyForm.description.trim(),
      registration_code: companyForm.registration_code.trim(),
      address: companyForm.address.trim(),
      contact_email: companyForm.contact_email.trim(),
      contact_phone: companyForm.contact_phone.trim(),
      website: companyForm.website.trim(),
      date_established: companyForm.date_established || null,
    });
    company.value = updated;
    isEditingCompany.value = false;
    showToast('Įmonės duomenys atnaujinti.', 'success');
  } catch {
    showToast('Nepavyko išsaugoti pakeitimų.', 'error');
  } finally {
    isSavingCompany.value = false;
  }
}

function openPosting(id: string) {
  router.push({ name: ROUTE_NAMES.EMPLOYER_JOB_POSTING_EDIT, params: { id } });
}

function goToNewPosting() {
  router.push({ name: ROUTE_NAMES.EMPLOYER_JOB_POSTING_NEW });
}

const cloningId = ref<string | null>(null);
const deletingId = ref<string | null>(null);

async function clonePosting(id: string) {
  cloningId.value = id;

  try {
    await jobPostingApi.clone(id);
    showToast('Skelbimas nukopijuotas kaip juodraštis.', 'success');
    await loadPostings(postingsPage.value);
  } catch {
    showToast('Nepavyko nukopijuoti skelbimo.', 'error');
  } finally {
    cloningId.value = null;
  }
}

async function deletePosting(id: string, title: string) {
  if (!window.confirm(`Ar tikrai norite ištrinti skelbimą „${title}“?`)) {
    return;
  }

  deletingId.value = id;

  try {
    await jobPostingApi.delete(id);
    showToast('Skelbimas ištrintas.', 'success');

    const remainingOnPage = postings.value.length - 1;
    const targetPage =
      remainingOnPage === 0 && postingsPage.value > 1
        ? postingsPage.value - 1
        : postingsPage.value;
    await loadPostings(targetPage);
  } catch {
    showToast('Nepavyko ištrinti skelbimo.', 'error');
  } finally {
    deletingId.value = null;
  }
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString('lt-LT');
}

function formatSalary(min: number | null, max: number | null) {
  if (min == null && max == null) {
    return '—';
  }

  if (min != null && max != null) {
    return `${min} – ${max} €`;
  }

  if (min != null) {
    return `nuo ${min} €`;
  }

  return `iki ${max} €`;
}

onMounted(() => {
  void loadCompany();
  void loadPostings(1);
});
</script>

<template>
  <section v-if="user" class="space-y-6">
    <div>
      <p class="text-sm font-semibold uppercase tracking-wide text-secondary">
        Darbdavio paskyra
      </p>
      <h1 class="mt-2 text-3xl font-bold text-gray-950">
        Sveiki, {{ user.first_name || user.email }}
      </h1>
    </div>

    <article class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
      <button
        class="flex w-full items-center justify-between gap-3 text-left"
        type="button"
        :aria-expanded="isUserInfoExpanded"
        @click="isUserInfoExpanded = !isUserInfoExpanded">
        <span class="text-xs font-semibold uppercase tracking-wide text-secondary">
          Naudotojo informacija
        </span>
        <span
          class="text-xs font-semibold text-gray-500 transition"
          :class="{ 'rotate-180': isUserInfoExpanded }">
          ▾
        </span>
      </button>
      <dl v-if="isUserInfoExpanded" class="mt-3 grid gap-3 sm:grid-cols-2">
        <div>
          <dt class="text-xs text-gray-500">Vardas, pavardė</dt>
          <dd class="text-sm font-medium text-gray-950">
            {{ user.first_name }} {{ user.last_name }}
          </dd>
        </div>
        <div>
          <dt class="text-xs text-gray-500">El. paštas</dt>
          <dd class="text-sm font-medium text-gray-950">{{ user.email }}</dd>
        </div>
        <div>
          <dt class="text-xs text-gray-500">Rolė</dt>
          <dd class="text-sm font-medium text-gray-950">{{ getRoleLabel(user.role) }}</dd>
        </div>
        <div>
          <dt class="text-xs text-gray-500">Paskyra sukurta</dt>
          <dd class="text-sm font-medium text-gray-950">
            {{ formatDate(user.created_at) }}
          </dd>
        </div>
      </dl>
    </article>

    <article class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
      <div class="flex items-start justify-between">
        <p class="text-xs font-semibold uppercase tracking-wide text-secondary">
          Įmonės informacija
        </p>
        <button
          v-if="!isEditingCompany && company"
          class="rounded-md bg-primary px-3 py-1.5 text-sm font-semibold text-attention transition hover:bg-secondary"
          type="button"
          @click="startEditCompany">
          Redaguoti
        </button>
      </div>

      <p v-if="isCompanyLoading" class="mt-3 text-sm text-gray-600">Kraunama...</p>

      <p v-else-if="!company" class="mt-3 text-sm text-gray-600">
        Įmonės profilio nėra.
      </p>

      <div v-else-if="!isEditingCompany" class="mt-3 space-y-3">
        <h2 class="text-lg font-semibold text-gray-950">{{ company.name }}</h2>
        <p class="whitespace-pre-line text-sm text-gray-700">
          {{ company.description || 'Aprašymas dar nepateiktas.' }}
        </p>
        <dl class="grid gap-3 sm:grid-cols-2">
          <div>
            <dt class="text-xs text-gray-500">Įmonės kodas</dt>
            <dd class="text-sm font-medium text-gray-950">
              {{ company.registration_code || '—' }}
            </dd>
          </div>
          <div>
            <dt class="text-xs text-gray-500">Įsteigimo data</dt>
            <dd class="text-sm font-medium text-gray-950">
              {{ company.date_established ? formatDate(company.date_established) : '—' }}
            </dd>
          </div>
          <div>
            <dt class="text-xs text-gray-500">Adresas</dt>
            <dd class="text-sm font-medium text-gray-950">{{ company.address || '—' }}</dd>
          </div>
          <div>
            <dt class="text-xs text-gray-500">Kontaktinis el. paštas</dt>
            <dd class="text-sm font-medium text-gray-950">
              <a
                v-if="company.contact_email"
                class="text-attention underline-offset-4 hover:underline"
                :href="`mailto:${company.contact_email}`">
                {{ company.contact_email }}
              </a>
              <span v-else>—</span>
            </dd>
          </div>
          <div>
            <dt class="text-xs text-gray-500">Kontaktinis telefonas</dt>
            <dd class="text-sm font-medium text-gray-950">
              <a
                v-if="company.contact_phone"
                class="text-attention underline-offset-4 hover:underline"
                :href="`tel:${company.contact_phone}`">
                {{ company.contact_phone }}
              </a>
              <span v-else>—</span>
            </dd>
          </div>
          <div>
            <dt class="text-xs text-gray-500">Svetainė / socialinis tinklas</dt>
            <dd class="text-sm font-medium text-gray-950">
              <a
                v-if="company.website"
                class="text-attention underline-offset-4 hover:underline"
                :href="company.website"
                rel="noopener noreferrer"
                target="_blank">
                {{ company.website }}
              </a>
              <span v-else>—</span>
            </dd>
          </div>
        </dl>
      </div>

      <form v-else class="mt-3 grid gap-3" @submit.prevent="saveCompany">
        <label class="block">
          <span class="text-sm font-medium text-gray-700">Pavadinimas</span>
          <input
            v-model="companyForm.name"
            class="mt-1 h-11 w-full rounded-md border border-gray-300 px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            placeholder="Įmonės pavadinimas"
            required
            type="text" />
        </label>
        <label class="block">
          <span class="text-sm font-medium text-gray-700">
            Įmonės kodas <span class="text-red-600">*</span>
          </span>
          <input
            v-model="companyForm.registration_code"
            class="mt-1 h-11 w-full rounded-md border border-gray-300 px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            placeholder="Pvz. 123456789"
            required
            type="text" />
        </label>
        <label class="block">
          <span class="text-sm font-medium text-gray-700">Aprašymas</span>
          <textarea
            v-model="companyForm.description"
            class="mt-1 min-h-24 w-full resize-y rounded-md border border-gray-300 px-3 py-2 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
            placeholder="Trumpai aprašykite įmonę"></textarea>
        </label>
        <div class="grid gap-3 sm:grid-cols-2">
          <label class="block">
            <span class="text-sm font-medium text-gray-700">Adresas</span>
            <input
              v-model="companyForm.address"
              class="mt-1 h-11 w-full rounded-md border border-gray-300 px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
              placeholder="Pvz. Gedimino pr. 1, Vilnius"
              type="text" />
          </label>
          <label class="block">
            <span class="text-sm font-medium text-gray-700">Įsteigimo data</span>
            <input
              v-model="companyForm.date_established"
              class="mt-1 h-11 w-full rounded-md border border-gray-300 px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
              type="date" />
          </label>
          <label class="block">
            <span class="text-sm font-medium text-gray-700">Kontaktinis el. paštas</span>
            <input
              v-model="companyForm.contact_email"
              class="mt-1 h-11 w-full rounded-md border border-gray-300 px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
              placeholder="kontaktai@imone.lt"
              type="email" />
          </label>
          <label class="block">
            <span class="text-sm font-medium text-gray-700">Kontaktinis telefonas</span>
            <input
              v-model="companyForm.contact_phone"
              class="mt-1 h-11 w-full rounded-md border border-gray-300 px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
              placeholder="+370 ..."
              type="tel" />
          </label>
          <label class="block sm:col-span-2">
            <span class="text-sm font-medium text-gray-700">
              Svetainė ar socialinio tinklo nuoroda
            </span>
            <input
              v-model="companyForm.website"
              class="mt-1 h-11 w-full rounded-md border border-gray-300 px-3 text-gray-950 outline-none transition placeholder:text-gray-400 focus:border-secondary focus:ring-2 focus:ring-secondary/40"
              placeholder="https://..."
              type="url" />
          </label>
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            class="rounded-md bg-attention px-4 py-2 text-sm font-semibold text-white transition hover:bg-secondary disabled:opacity-60"
            :disabled="isSavingCompany"
            type="submit">
            Išsaugoti
          </button>
          <button
            class="rounded-md bg-gray-100 px-4 py-2 text-sm font-semibold text-gray-700 transition hover:bg-gray-200"
            type="button"
            @click="cancelEditCompany">
            Atšaukti
          </button>
        </div>
      </form>
    </article>

    <section class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
      <div class="flex items-start justify-between gap-3">
        <div>
          <p class="text-xs font-semibold uppercase tracking-wide text-secondary">
            Darbo skelbimai
          </p>
          <h2 class="mt-1 text-lg font-semibold text-gray-950">
            Skelbimų sąrašas
            <span v-if="postingsTotal > 0" class="ml-1 text-sm font-normal text-gray-500">
              ({{ postingsTotal }})
            </span>
          </h2>
        </div>
        <button
          v-if="postings.length > 0"
          class="rounded-md bg-attention px-3 py-1.5 text-sm font-semibold text-white transition hover:bg-secondary"
          type="button"
          @click="goToNewPosting">
          Naujas skelbimas
        </button>
      </div>

      <p v-if="isPostingsLoading" class="mt-3 text-sm text-gray-600">Kraunama...</p>

      <div
        v-else-if="postings.length === 0"
        class="mt-4 flex flex-col items-center gap-3 rounded-md border border-dashed border-gray-300 bg-background/40 px-4 py-8 text-center">
        <p class="text-sm text-gray-700">Skelbimų kol kas nėra.</p>
        <button
          class="rounded-md bg-attention px-4 py-2 text-sm font-semibold text-white transition hover:bg-secondary"
          type="button"
          @click="goToNewPosting">
          Sukurti pirmą skelbimą
        </button>
      </div>

      <div v-else class="mt-4 overflow-x-auto">
        <table class="w-full border-collapse text-left text-sm">
          <thead>
            <tr class="border-b border-gray-200 text-xs uppercase tracking-wide text-gray-500">
              <th class="py-2 pr-3 font-semibold">Pavadinimas</th>
              <th class="py-2 pr-3 font-semibold">Sritis</th>
              <th class="py-2 pr-3 font-semibold">Tipas</th>
              <th class="py-2 pr-3 font-semibold">Būsena</th>
              <th class="py-2 pr-3 font-semibold">Atlyginimas</th>
              <th class="py-2 pr-3 font-semibold">Sukurta</th>
              <th class="py-2 font-semibold text-right">Veiksmai</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="posting in postings"
              :key="posting.id"
              class="cursor-pointer border-b border-gray-100 transition hover:bg-background/60"
              @click="openPosting(posting.id)">
              <td class="py-3 pr-3 font-medium text-gray-950">{{ posting.title }}</td>
              <td class="py-3 pr-3 text-gray-700">{{ posting.industry_name }}</td>
              <td class="py-3 pr-3 text-gray-700">
                {{ JOB_TYPE_LABELS[posting.job_type] }}
              </td>
              <td class="py-3 pr-3">
                <span
                  class="rounded-full px-2 py-0.5 text-xs font-semibold"
                  :class="{
                    'bg-primary text-attention': posting.status === 'open',
                    'bg-gray-200 text-gray-700': posting.status === 'draft',
                    'bg-red-100 text-red-700': posting.status === 'closed',
                  }">
                  {{ JOB_STATUS_LABELS[posting.status] }}
                </span>
              </td>
              <td class="py-3 pr-3 text-gray-700">
                {{ formatSalary(posting.salary_min, posting.salary_max) }}
              </td>
              <td class="py-3 pr-3 text-gray-700">{{ formatDate(posting.created_at) }}</td>
              <td class="py-3 text-right">
                <div class="flex justify-end gap-2">
                  <button
                    class="rounded-md bg-primary px-2.5 py-1 text-xs font-semibold text-attention transition hover:bg-secondary disabled:opacity-50"
                    :disabled="cloningId === posting.id"
                    type="button"
                    @click.stop="clonePosting(posting.id)">
                    {{ cloningId === posting.id ? 'Kopijuojama...' : 'Klonuoti' }}
                  </button>
                  <button
                    class="rounded-md bg-gray-100 px-2.5 py-1 text-xs font-semibold text-gray-700 transition hover:bg-gray-200 disabled:opacity-50"
                    :disabled="deletingId === posting.id"
                    type="button"
                    @click.stop="deletePosting(posting.id, posting.title)">
                    {{ deletingId === posting.id ? 'Trinama...' : 'Ištrinti' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="totalPages > 1" class="mt-4 flex items-center justify-between text-sm">
          <button
            class="rounded-md bg-gray-100 px-3 py-1.5 font-semibold text-gray-700 transition hover:bg-gray-200 disabled:opacity-50"
            :disabled="!postingsPrevious"
            type="button"
            @click="loadPostings(postingsPage - 1)">
            ← Atgal
          </button>
          <span class="text-gray-600">
            Puslapis {{ postingsPage }} iš {{ totalPages }}
          </span>
          <button
            class="rounded-md bg-gray-100 px-3 py-1.5 font-semibold text-gray-700 transition hover:bg-gray-200 disabled:opacity-50"
            :disabled="!postingsNext"
            type="button"
            @click="loadPostings(postingsPage + 1)">
            Pirmyn →
          </button>
        </div>
      </div>
    </section>
  </section>
  <section v-else class="rounded-lg bg-white p-6 text-gray-700 shadow-sm">
    Paskyros būsena atnaujinama.
  </section>
</template>
