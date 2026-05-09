import { toast } from "sonner"
import { Button } from "~/components/ui/button"
import { Card, CardContent } from "~/components/ui/card"
import {
  Field,
  FieldGroup,
  FieldLabel
} from "~/components/ui/field"
import { Input } from "~/components/ui/input"
import { type UserType } from "~/contexts/auth-context"
import api from "~/lib/api"
import { cn } from "~/lib/utils"

export function ForgotPasswordForm({
  className,
  user,
  ...props
}: { user: UserType } & React.ComponentProps<"div">) {

  const sendResetLink = async (data: FormData) => {
    const email = data.get("email")?.toString()

    if (!email) {
      toast.warning("Warning", {
        description: "Please provide email."
      })
      return
    }

    const forgotPasswordApi = user === 'seller' ? api.seller.forgortPassword : api.partner.forgotPassword
    await forgotPasswordApi({ email })

    toast.success("Success", {
      description: `Reset link has been sent to ${email}.`
    })
  }


  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card className="overflow-hidden p-0">
        <CardContent className="grid p-0 md:grid-cols-2">
          <form className="p-6 md:p-8" action={sendResetLink}>
            <FieldGroup>
              <div className="flex flex-col items-center gap-2 text-center">
                <h1 className="text-2xl font-bold">Reset Password</h1>
                <p className="text-balance text-muted-foreground">
                  Enter your email address
                </p>
              </div>
              <Field>
                <FieldLabel htmlFor="email">Email <span className="text-red-600">*</span></FieldLabel>
                <Input
                  name="email"
                  id="email"
                  type="email"
                  placeholder="example@gmail.com"
                  required
                  className="min-h-11"
                />
              </Field>
              <Field>
                <Button type="submit" className="cursor-pointer min-h-11">Send Reset Link</Button>
              </Field>
            </FieldGroup>
          </form>
          <div className="relative hidden bg-muted md:block">
            <img
              src="/placeholder.svg"
              alt="Image"
              className="absolute inset-0 h-full w-full object-cover dark:brightness-[0.2] dark:grayscale"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
