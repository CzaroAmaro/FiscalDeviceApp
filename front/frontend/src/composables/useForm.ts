import type { Ref } from 'vue';
import { computed,reactive, ref } from 'vue';
import type { VForm } from 'vuetify/components';

export type FormPayload = Record<string, unknown>;
export type EditableItem<TId extends number = number> = { id: TId } | null;
export type TransformPayloadFn<T extends FormPayload> = (payload: T) => T;
export type TransformItemToPayloadFn<TItem, TPayload> = (item: TItem) => Partial<TPayload>;

export function useForm<
  TPayload extends FormPayload,
  TItem extends EditableItem = EditableItem,
  TResult = TItem | void
>(
  initialData: TPayload,
  editingItem: Ref<TItem>,
  addFn: (payload: TPayload) => Promise<TResult>,
  updateFn: (id: number, payload: TPayload) => Promise<TResult>,
  transformPayloadForApi?: TransformPayloadFn<TPayload>,
  transformItemToForm?: TransformItemToPayloadFn<TItem, TPayload>
) {
  const formRef = ref<VForm | null>(null);
  const formData = reactive({ ...initialData } as TPayload);
  const state = reactive({
    isSaving: false,
    error: null as string | null,
  });

  const isEditing = computed(() => !!editingItem.value);

  function resetForm() {
    state.error = null;
    if (isEditing.value && editingItem.value) {
      Object.assign(formData, initialData);

      if (transformItemToForm) {
        const transformedData = transformItemToForm(editingItem.value);
        Object.assign(formData, transformedData);
      } else {
        Object.assign(formData, editingItem.value as unknown as TPayload);
      }
    } else {
      Object.assign(formData, initialData);
    }
  }

  async function submit(): Promise<TResult> {
    if (!formRef.value) {
      throw new Error('Form ref not found');
    }

    const valid = await formRef.value.validate();
    if (!valid.valid) {
      throw new Error('Walidacja formularza nie powiodła się.');
    }

    state.isSaving = true;
    state.error = null;

    try {
      let payload = { ...formData } as TPayload;

      if (transformPayloadForApi) {
        payload = transformPayloadForApi(payload);
      }

      if (isEditing.value && editingItem.value) {
        return await updateFn(editingItem.value.id, payload);
      } else {
        return await addFn(payload);
      }
    } catch (err: unknown) {
      try {
        const anyErr = err as Record<string, unknown>;
        const response = anyErr.response as Record<string, unknown> | undefined;
        const data = response?.data as Record<string, unknown> | undefined;
        if (data && typeof data === 'object') {
          const firstKey = Object.keys(data)[0];
          const rawFirst = data[firstKey];
          const message =
            Array.isArray(rawFirst) && rawFirst.length > 0 ? String(rawFirst[0]) : String(rawFirst);
          state.error = `${firstKey}: ${message}`;
        } else if (anyErr.message && typeof anyErr.message === 'string') {
          state.error = anyErr.message;
        } else {
          state.error = 'Wystąpił nieoczekiwany błąd.';
        }
      } catch {
        state.error = 'Wystąpił nieoczekiwany błąd.';
      }
      throw err;
    } finally {
      state.isSaving = false;
    }
  }

  return {
    formRef,
    formData,
    state,
    isEditing,
    resetForm,
    submit,
  } as const;
}
