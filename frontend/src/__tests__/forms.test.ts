import { clientSchema, engineSchema, validate } from "../lib/forms";

describe("form validation", () => {
  it("accepts a valid client and drops empty optional fields", () => {
    const result = validate(clientSchema, {
      name: " Mina Andina ",
      document_type: "NIT",
      document_number: "900123456",
      email: "",
      phone: "",
    });
    expect(result.errors).toBeNull();
    expect(result.data).toEqual({ name: "Mina Andina", document_type: "NIT", document_number: "900123456" });
  });

  it("reports one message per invalid field", () => {
    const result = validate(clientSchema, { name: "", document_type: "", document_number: "1", email: "x", phone: "" });
    expect(Object.keys(result.errors ?? {}).sort()).toEqual(["document_number", "document_type", "email", "name"]);
  });

  it("requires an owner for engines", () => {
    const result = validate(engineSchema, {
      serial_number: "CAT-1",
      manufacturer: "Caterpillar",
      model: "3516",
      engine_type: "Diesel",
      capacity: "",
      client_id: "",
    });
    expect(result.errors?.client_id).toBe("Selecciona el cliente propietario");
  });
});
