import { PageHeader } from "@/components/PageHeader";
import { SimulatorClient } from "./SimulatorClient";

export default function SimulatorPage() {
  return (
    <div>
      <PageHeader title="Call Simulator" description="Generate English and Hindi demo calls through the same live intent and branch logic used by production calls." />
      <SimulatorClient />
    </div>
  );
}
