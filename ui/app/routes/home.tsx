import type { Route } from "./+types/home";
import { Welcome } from "../welcome/welcome";
import { Button } from "~/components/ui/button";
import { Link } from "react-router";

export function meta({ }: Route.MetaArgs) {
  return [
    { title: "New React Router App" },
    { name: "description", content: "Welcome to React Router!" },
  ];
}

export default function Home() {
  return (
    <section className="flex flex-col min-h-screen space-y-4 items-center justify-center">
      <h1 className="text-5xl font-bold">Welcome to FastShip</h1>
      <h3>Start your journey with us right now!</h3>
      <div className="flex items-center justify-center gap-4">
        <Button type="button" className="min-h-11 cursor-pointer" asChild>
          <Link to="/seller/login">Seller Loign</Link>
        </Button>
        <Button className="min-h-11 cursor-pointer" type="button" variant="secondary">
          <Link to="/partner/login">Partner Login</Link>
        </Button>
      </div>
    </section>
  );
}
