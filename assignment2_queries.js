// Assignment 2a - MongoDB restaurant queries
// Run with: mongosh --file "C:\\Users\\shanm\\Downloads\\myassignment\\assignment2_queries.js"

const assignmentDB = db.getSiblingDB("assignment2");
const restaurants = assignmentDB.getCollection("restaurants");

function heading(number, title) {
  print(`\n================ Q${number}: ${title} ================`);
}

function printSample(cursor, size = 10) {
  cursor.limit(size).forEach((document) => printjson(document));
}

heading(1, "Restaurant ID, name, borough, and zip code");
print(`Total documents: ${restaurants.countDocuments({})}`);
print("Showing the first 5 documents:");
printSample(
  restaurants.find(
    {},
    {
      _id: 0,
      restaurant_id: 1,
      name: 1,
      borough: 1,
      "address.zipcode": 1
    }
  ),
  5
);

heading(2, "First 5 restaurants in the Bronx");
printSample(restaurants.find({ borough: "Bronx" }), 5);

heading(3, "Restaurants with a score greater than 80 and less than 100");
const q3Filter = {
  grades: { $elemMatch: { score: { $gt: 80, $lt: 100 } } }
};
print(`Total matches: ${restaurants.countDocuments(q3Filter)}`);
printSample(
  restaurants.find(q3Filter, {
    _id: 0,
    restaurant_id: 1,
    name: 1,
    borough: 1,
    cuisine: 1,
    grades: { $elemMatch: { score: { $gt: 80, $lt: 100 } } }
  }),
  20
);

heading(4, "Restaurants whose name contains 'Reg'");
const q4Filter = { name: /Reg/ };
print(`Total matches: ${restaurants.countDocuments(q4Filter)}`);
printSample(
  restaurants.find(q4Filter, {
    _id: 0,
    restaurant_id: 1,
    name: 1,
    borough: 1,
    cuisine: 1
  }),
  10
);

heading(5, "Cuisine ascending and borough descending");
print(`Total documents: ${restaurants.countDocuments({})}`);
print("Showing the first 20 sorted documents:");
printSample(
  restaurants
    .find({}, { _id: 0, restaurant_id: 1, name: 1, cuisine: 1, borough: 1 })
    .sort({ cuisine: 1, borough: -1 }),
  20
);

heading(6, "Restaurants with at least one grade score below 5");
const q6Filter = { "grades.score": { $lt: 5 } };
print(`Total matches: ${restaurants.countDocuments(q6Filter)}`);
printSample(
  restaurants.find(q6Filter, {
    _id: 0,
    restaurant_id: 1,
    name: 1,
    borough: 1,
    cuisine: 1,
    grades: 1
  }),
  10
);

heading(7, "Manhattan restaurants having scores of both 2 and 6");
const q7Filter = {
  borough: "Manhattan",
  "grades.score": { $all: [2, 6] }
};
print(`Total matches: ${restaurants.countDocuments(q7Filter)}`);
printSample(
  restaurants.find(q7Filter, {
    _id: 0,
    restaurant_id: 1,
    name: 1,
    borough: 1,
    cuisine: 1,
    grades: 1
  }),
  10
);

heading(8, "Highest score for each restaurant");
print("Showing the 10 restaurants with the highest maximum score:");
printSample(
  restaurants.aggregate([
    {
      $project: {
        _id: 0,
        restaurant_id: 1,
        name: 1,
        highest_score: { $max: "$grades.score" }
      }
    },
    { $sort: { highest_score: -1, name: 1 } }
  ]),
  10
);

heading(9, "Restaurants having at least one A grade and one B grade");
const q9Filter = { "grades.grade": { $all: ["A", "B"] } };
print(`Total matches: ${restaurants.countDocuments(q9Filter)}`);
printSample(
  restaurants.find(q9Filter, {
    _id: 0,
    name: 1,
    address: 1
  }),
  10
);

heading(10, "Turkish restaurant with the highest average score");
restaurants
  .aggregate([
    { $match: { cuisine: "Turkish" } },
    {
      $project: {
        _id: 0,
        restaurant_id: 1,
        name: 1,
        borough: 1,
        cuisine: 1,
        average_score: { $avg: "$grades.score" }
      }
    },
    { $sort: { average_score: -1 } },
    { $limit: 1 }
  ])
  .forEach((document) => printjson(document));

print("\nAll 10 queries completed.");
