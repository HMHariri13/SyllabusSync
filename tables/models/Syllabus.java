import java.time.LocalDateTime;

public class Syllabus {

    private long id;
    private long userId; // Foreign key for the User
    private String courseName;
    private String term;
    private String rawText;
    private LocalDateTime uploadedAt;

    // Constructor for creating new syllabi
    public Syllabus(long userId, String courseName, String term, String rawText) {
        this.userId = userId;
        this.courseName = courseName;
        this.term = term;
        this.rawText = rawText;
    }

    // Full constructor for retrieving from DB
    public Syllabus(long id, long userId, String courseName, String term, String rawText, LocalDateTime uploadedAt) {
        this.id = id;
        this.userId = userId;
        this.courseName = courseName;
        this.term = term;
        this.rawText = rawText;
        this.uploadedAt = uploadedAt;
    }

    // Getters and Setters
    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }

    public long getUserId() {
        return userId;
    }

    public void setUserId(long userId) {
        this.userId = userId;
    }

    public String getCourseName() {
        return courseName;
    }

    public void setCourseName(String courseName) {
        this.courseName = courseName;
    }

    public String getTerm() {
        return term;
    }

    public void setTerm(String term) {
        this.term = term;
    }

    public String getRawText() {
        return rawText;
    }

    public void setRawText(String rawText) {
        this.rawText = rawText;
    }

    public LocalDateTime getUploadedAt() {
        return uploadedAt;
    }

    public void setUploadedAt(LocalDateTime uploadedAt) {
        this.uploadedAt = uploadedAt;
    }
}