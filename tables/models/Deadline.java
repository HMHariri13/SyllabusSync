import java.time.LocalDate;

public class Deadline {

    private long id;
    private long syllabusId; // Foreign key for the Syllabus
    private String taskType;
    private String taskName;
    private LocalDate dueDate;
    private String weight;
    private String notes;

    // Constructor for creating new deadlines
    public Deadline(long syllabusId, String taskType, String taskName, LocalDate dueDate, String weight, String notes) {
        this.syllabusId = syllabusId;
        this.taskType = taskType; //Type of task    
        this.taskName = taskName; //Name of task    
        this.dueDate = dueDate; //Date
        this.weight = weight; //Percentage of grade
        this.notes = notes; //Additional info
    }

    // Full constructor for retrieving from DB
    public Deadline(long id, long syllabusId, String taskType, String taskName, LocalDate dueDate, String weight, String notes) {
        this.id = id;
        this.syllabusId = syllabusId;
        this.taskType = taskType;
        this.taskName = taskName;
        this.dueDate = dueDate;
        this.weight = weight;
        this.notes = notes;
    }

    // Getters and Setters
    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }

    public long getSyllabusId() {
        return syllabusId;
    }

    public void setSyllabusId(long syllabusId) {
        this.syllabusId = syllabusId;
    }

    public String getTaskType() {
        return taskType;
    }

    public void setTaskType(String taskType) {
        this.taskType = taskType;
    }

    public String getTaskName() {
        return taskName;
    }

    public void setTaskName(String taskName) {
        this.taskName = taskName;
    }

    public LocalDate getDueDate() {
        return dueDate;
    }

    public void setDueDate(LocalDate dueDate) {
        this.dueDate = dueDate;
    }

    public String getWeight() {
        return weight;
    }

    public void setWeight(String weight) {
        this.weight = weight;
    }

    public String getNotes() {
        return notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
    }
}