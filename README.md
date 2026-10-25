# MongoDB Queries

[![Validation](https://github.com/thillainirmal-tech/mongodb-queries/actions/workflows/validate.yml/badge.svg)](https://github.com/thillainirmal-tech/mongodb-queries/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/thillainirmal-tech/mongodb-queries)](LICENSE)

Practical MongoDB data-modeling exercises using a public restaurant dataset. The project contains ten reproducible queries, a report generator, and the completed assignment report.

## Contents

- `assignment2_queries.js` — ten queries covering filters, projections, sorting, arrays, and aggregation.
- `restaurants.json` — sample restaurant data used by the exercises.
- `build_assignment_pdf.py` — generates the formatted report.
- `output/pdf/Data_Modelling_Assignment_2a.pdf` — generated assignment report.
- `Assgn2a.pdf` — original assignment brief.

## Run the queries

Import the dataset into a local MongoDB instance:

```bash
mongoimport --db assignment2 --collection restaurants --file restaurants.json
```

Then execute all ten queries:

```bash
mongosh --file assignment2_queries.js
```

## Generate the report

```bash
python -m pip install reportlab
python build_assignment_pdf.py
```

The generated document is written to `output/pdf/Data_Modelling_Assignment_2a.pdf`.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes. Report security issues using the process in [SECURITY.md](SECURITY.md).

## License

Licensed under the [MIT License](LICENSE).
