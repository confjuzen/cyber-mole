package com.retromedia;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.commons.io.FileUtils;
import spark.Request;
import spark.Response;
import spark.Spark;
import smile.data.DataFrame;
import smile.data.vector.StringVector;
import smile.regression.RandomForest;
import smile.regression.Regression;
import java.io.File;
import java.io.IOException;
import java.util.*;
import smile.data.format.CsvFormat;

public class SmileService {
    private static final ObjectMapper mapper = new ObjectMapper();
    private Regression<smile.data.vector.DoubleVector> model;

    public static void main(String[] args) {
        Spark.port(9000);
        new SmileService().initRoutes();
        System.out.println("Smile service started on port 9000");
    }

    private void initRoutes() {
        Spark.post("/clean", this::cleanData);
        Spark.post("/train/predict_sales", this::trainModel);
        Spark.post("/predict", this::predictSales);
    }

    private String cleanData(Request req, Response res) throws IOException {
        // Assume JSON or CSV input; for simplicity, parse as CSV string
        String data = req.body();
        DataFrame df = DataFrame.of(data); // Basic Smile DataFrame creation
        // Cleaning: normalize strings, fill missing, detect duplicates
        df = cleanDataFrame(df);
        String cleaned = df.toString(); // Export as CSV-like
        return mapper.writeValueAsString(Map.of("cleanedData", cleaned, "rowsCleaned", df.size()));
    }

    private DataFrame cleanDataFrame(DataFrame df) {
        // Normalize artist names: lowercase, trim
        if (df.column("artist") != null) {
            StringVector artist = (StringVector) df.column("artist").map(s -> s.toLowerCase().trim());
            df = df.replace("artist", artist);
        }
        // Fill missing price with average
        if (df.column("price") != null) {
            double avgPrice = df.column("price").stream().mapToDouble(v -> v.isDouble() ? v.asDouble() : 0).average().orElse(0);
            df = df.replace("price", df.column("price").map(v -> v.isDouble() ? v.asDouble() : avgPrice));
        }
        // Remove duplicates based on title + artist + format
        df = df.dropDuplicates("title", "artist", "format");
        return df;
    }

    private String trainModel(Request req, Response res) throws IOException {
        String data = req.body();
        DataFrame df = DataFrame.of(data);
        // Assume columns: genre, price, release_year, historical_sales
        double[][] features = df.stream().map(row -> new double[]{row.getDouble("price"), row.getDouble("release_year"), row.getDouble("historical_sales")}).toArray(double[][]::new);
        double[] labels = df.column("sales").toDoubleArray();
        model = RandomForest.fit(features, labels);
        Map<String, Object> metrics = Map.of("modelType", "RandomForest", "features", df.ncols() - 1, "samples", df.size());
        return mapper.writeValueAsString(metrics);
    }

    private String predictSales(Request req, Response res) throws IOException {
        Map<String, Double> input = mapper.readValue(req.body(), Map.class);
        double[] feature = {input.get("price"), input.get("release_year"), input.get("historical_sales")};
        double prediction = model.predict(feature);
        return mapper.writeValueAsString(Map.of("predictedSales", prediction));
    }
}