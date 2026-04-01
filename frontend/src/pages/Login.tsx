import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNavigate, useSearchParams, Navigate } from 'react-router-dom'
import { login } from '@/api/auth'
import { useAuthStore } from '@/store/authStore'

const schema = z.object({
  identifier: z.string().min(1, '필수 항목입니다.').max(100),
  password: z.string().min(1, '필수 항목입니다.').max(128),
})

type FormValues = z.infer<typeof schema>

export default function Login() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { role, setAuth } = useAuthStore()

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  if (role !== 'GUEST') {
    return <Navigate to="/" replace />
  }

  const onSubmit = async (values: FormValues) => {
    try {
      const data = await login(values)
      setAuth(data.accessToken, data.userId, data.role)
      const redirect = searchParams.get('redirect') ?? '/'
      navigate(redirect, { replace: true })
    } catch {
      setError('root', { message: '아이디 또는 비밀번호를 확인해 주세요.' })
    }
  }

  return (
    <div className="mx-auto mt-20 max-w-sm">
      <h1 className="mb-8 text-center text-2xl font-bold text-gray-900">로그인</h1>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">학번 / 이메일</label>
          <input
            {...register('identifier')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          {errors.identifier && (
            <p className="mt-1 text-xs text-red-500">{errors.identifier.message}</p>
          )}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">비밀번호</label>
          <input
            {...register('password')}
            type="password"
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          {errors.password && (
            <p className="mt-1 text-xs text-red-500">{errors.password.message}</p>
          )}
        </div>
        {errors.root && (
          <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-600">
            {errors.root.message}
          </p>
        )}
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full rounded-md bg-primary-600 py-2.5 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
        >
          {isSubmitting ? '로그인 중...' : '로그인'}
        </button>
      </form>
    </div>
  )
}
